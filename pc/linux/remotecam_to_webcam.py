#!/usr/bin/env python3
"""
=============================================================================
RemoteCam - Stream to Virtual Webcam (Linux)
=============================================================================
Enhanced version with:
- Auto-detection of phone IP
- Config file support (config.yaml)
- Video filters (rotation, effects, etc.)
- v4l2loopback output integrated

Requirements:
    pip install -r requirements.txt
    sudo apt install v4l2loopback-dkms
=============================================================================
"""

import cv2
import numpy as np
import argparse
import sys
import time
import os
import fcntl
from pathlib import Path

# Add parent directory to path to allow importing common modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from common.config_loader import load_config
    from common.network_scanner import find_remotecam
    from common.video_filters import create_filter_chain_from_args, apply_filters, AVAILABLE_FILTERS
except ImportError as e:
    print(f"Error importing common modules: {e}")
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description='RemoteCam to Virtual Webcam Stream (Linux)',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Connection args
    parser.add_argument('-i', '--ip', help='Phone IP address')
    parser.add_argument('-p', '--port', type=int, help='RemoteCam port')
    parser.add_argument('--auto-detect', action='store_true', help='Scan network for RemoteCam')
    
    # Config args
    parser.add_argument('-c', '--config', help='Path to config.yaml')
    
    # Device args
    parser.add_argument('-d', '--device', help='Virtual video device (e.g. /dev/video10)')
    
    # Video args
    parser.add_argument('--width', type=int, help='Output width')
    parser.add_argument('--height', type=int, help='Output height')
    parser.add_argument('--fps', type=int, help='Target FPS')
    
    # Output args
    parser.add_argument('--preview', action='store_true', help='Show preview window')
    
    # Filter args
    filter_help = "\n".join([f"  --{f}: Apply {f} filter" for f in AVAILABLE_FILTERS if f not in ['rotate', 'mirror']])
    
    parser.add_argument('--flip', choices=['none', 'horizontal', 'vertical', 'both'], help='Flip video')
    parser.add_argument('--rotate', type=int, choices=[0, 90, 180, 270], help='Rotate video (degrees)')
    parser.add_argument('--grayscale', action='store_true', help='Apply grayscale filter')
    parser.add_argument('--blur', type=int, help='Apply blur (strength 1-50)')
    parser.add_argument('--edge', action='store_true', help='Apply edge detection')
    parser.add_argument('--vintage', action='store_true', help='Apply vintage/sepia effect')
    parser.add_argument('--cartoon', action='store_true', help='Apply cartoon effect')
    parser.add_argument('--negative', action='store_true', help='Apply negative effect')
    parser.add_argument('--sharpen', action='store_true', help='Apply sharpening')
    parser.add_argument('--brightness', type=int, help='Adjust brightness (-100 to 100)')
    parser.add_argument('--contrast', type=int, help='Adjust contrast (-100 to 100)')
    
    return parser.parse_args()


def main():
    # Parse CLI args
    args = parse_args()
    
    # Load configuration
    cli_args = vars(args)
    cli_args = {k: v for k, v in cli_args.items() if v is not None}
    
    config = load_config(args.config, cli_args)
    
    print("=" * 60)
    print("  RemoteCam to V4L2Loopback (Linux Enhanced)")
    print("=" * 60)
    
    # 1. Network Discovery
    phone_ip = config.phone_ip
    
    if config.auto_detect:
        print("\n🔍 Auto-detecting RemoteCam on network...")
        found = find_remotecam(
            port=config.port,
            timeout=config.scan_timeout,
            prefer_ip=config.phone_ip
        )
        if found:
            phone_ip, port = found
            config.phone_ip = phone_ip
            config.port = port
            print(f"✅ Found RemoteCam at {phone_ip}:{port}")
        else:
            print("⚠️  No RemoteCam found via auto-detection.")
            print(f"   Using configured IP: {config.phone_ip}")
    
    # 2. Build Stream URL
    stream_url = config.get_stream_url()
    
    print(f"\nConfiguration:")
    print(f"  Stream URL:    {stream_url}")
    print(f"  Output:        {config.video_device}")
    print(f"  Resolution:    {config.width}x{config.height}")
    print(f"  FPS:           {config.fps}")
    
    # Check if virtual device exists
    if not os.path.exists(config.video_device):
        print(f"\n❌ Error: Virtual device {config.video_device} does not exist!")
        print("   Run setup_v4l2loopback.sh first to create the device.")
        sys.exit(1)
    
    # 3. Setup Filters
    filters = create_filter_chain_from_args(args)
    if config.rotate != 0 and not args.rotate:
        filters.insert(0, {'name': 'rotate', 'angle': config.rotate})
        
    if filters:
        print(f"  Active Filters: {', '.join([f.get('name') for f in filters])}")
        
    print("=" * 60)
    
    # 4. Connect to Stream
    print(f"\nConnecting to {stream_url}...")
    cap = cv2.VideoCapture(stream_url)
    
    if not cap.isOpened():
        print(f"\n❌ Error: Cannot connect to RemoteCam at {stream_url}")
        sys.exit(1)
            
    print("✅ Connected to stream!")
    
    # 5. Open Video Writer (V4L2)
    try:
        # Use YUYV format which is widely compatible
        fourcc = cv2.VideoWriter_fourcc(*'YUYV')
        out = cv2.VideoWriter(
            config.video_device,
            fourcc,
            config.fps,
            (config.width, config.height)
        )
        
        if not out.isOpened():
            print(f"❌ Error: Cannot open {config.video_device} for writing")
            print("   Check permissions or if device is in use.")
            sys.exit(1)
            
        print(f"🎥 Virtual webcam active at {config.video_device}")
            
    except Exception as e:
        print(f"❌ Error opening video writer: {e}")
        sys.exit(1)
    
    print("\n🚀 Streaming started! (Press 'q' to quit)")
        
    # Performance tracking
    frame_count = 0
    start_time = time.time()
    fps_display = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("⚠️  Lost connection, reconnecting...")
                cap.release()
                time.sleep(1)
                cap = cv2.VideoCapture(stream_url)
                continue
            
            # Resize
            if frame.shape[1] != config.width or frame.shape[0] != config.height:
                frame = cv2.resize(frame, (config.width, config.height))
            
            # Apply Filters
            if filters:
                frame = apply_filters(frame, filters)
            
            # Calculate FPS
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                fps_display = frame_count / elapsed
                frame_count = 0
                start_time = time.time()
            
            # Write to Virtual Device
            out.write(frame)
                
            # Preview Window
            if args.preview:
                preview_frame = frame.copy()
                
                # Overlay Info
                cv2.putText(
                    preview_frame,
                    f"FPS: {fps_display:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                
                cv2.imshow("RemoteCam Linux", preview_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                # Need slight sleep to maintain loop timing if no imshow
                time.sleep(1.0 / (config.fps + 5))
                    
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print("Done.")


if __name__ == "__main__":
    main()
