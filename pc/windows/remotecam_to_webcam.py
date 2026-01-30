#!/usr/bin/env python3
"""
=============================================================================
RemoteCam - Stream to Virtual Webcam (Windows)
=============================================================================
Enhanced version with:
- Auto-detection of phone IP
- Config file support (config.yaml)
- Video filters (rotation, effects, etc.)
- Virtual camera output integrated
- Hand Tracking Mouse Control (NEW)

Requirements:
    pip install -r requirements.txt
=============================================================================
"""

import cv2
import numpy as np
import argparse
import sys
import time
import os
from pathlib import Path

# Force UTF-8 for stdout on Windows to support emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path to allow importing common modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from common.config_loader import load_config
    from common.network_scanner import find_remotecam
    from common.video_filters import create_filter_chain_from_args, apply_filters, AVAILABLE_FILTERS
    
    # Optional Hand Tracking imports
    try:
        from common.hand_tracking import HandTracker
        from common.mouse_controller import MouseController
        HAND_TRACKING_AVAILABLE = True
    except ImportError:
        HAND_TRACKING_AVAILABLE = False
        
    COMMON_AVAILABLE = True
except ImportError as e:
    print(f"Error importing common modules: {e}")
    COMMON_AVAILABLE = False
    sys.exit(1)

# Try to import pyvirtualcam
try:
    import pyvirtualcam
    PYVIRTUALCAM_AVAILABLE = True
except ImportError:
    PYVIRTUALCAM_AVAILABLE = False


def parse_args():
    parser = argparse.ArgumentParser(
        description='RemoteCam to Virtual Webcam Stream (Windows)',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Connection args
    parser.add_argument('-i', '--ip', help='Phone IP address')
    parser.add_argument('-p', '--port', type=int, help='RemoteCam port')
    parser.add_argument('--auto-detect', action='store_true', help='Scan network for RemoteCam')
    
    # Config args
    parser.add_argument('-c', '--config', help='Path to config.yaml')
    
    # Video args
    parser.add_argument('--width', type=int, help='Output width')
    parser.add_argument('--height', type=int, help='Output height')
    parser.add_argument('--fps', type=int, help='Target FPS')
    
    # Mouse Control args
    parser.add_argument('--mouse-control', action='store_true', help='Enable Hand Tracking Mouse Control')
    parser.add_argument('--smoothing', type=float, default=0.7, help='Mouse smoothing factor (0.0-0.9)')
    
    # Output args
    parser.add_argument('--preview', action='store_true', help='Show preview window')
    parser.add_argument('--no-virtual-cam', action='store_true', help='Disable virtual camera output')
    
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
    print("  RemoteCam to Virtual Webcam (Windows Enhanced)")
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
    print(f"  Resolution:    {config.width}x{config.height}")
    print(f"  FPS:           {config.fps}")
    print(f"  Virtual Cam:   {'Enabled' if not args.no_virtual_cam and PYVIRTUALCAM_AVAILABLE else 'Disabled'}")
    
    # 3. Setup Filters & Features
    filters = create_filter_chain_from_args(args)
    if config.rotate != 0 and not args.rotate:
        filters.insert(0, {'name': 'rotate', 'angle': config.rotate})
    
    if filters:
        print(f"  Active Filters: {', '.join([f.get('name') for f in filters])}")

    # Setup Hand Tracking
    hand_tracker = None
    mouse = None
    use_mouse_control = args.mouse_control
    
    if use_mouse_control:
        if HAND_TRACKING_AVAILABLE:
            print("🖱️  Mouse Control:  ENABLED")
            hand_tracker = HandTracker(detection_conf=0.7, tracking_conf=0.7)
            mouse = MouseController(smoothing=args.smoothing)
        else:
            print("⚠️  Mouse Control:  DISABLED (mediapipe/pyautogui missing)")
            use_mouse_control = False
    
    print("=" * 60)
    
    # Check for pyvirtualcam
    if not PYVIRTUALCAM_AVAILABLE and not args.no_virtual_cam:
        print("\nNote: pyvirtualcam not installed. Virtual camera output disabled.")
    
    # 4. Connect to Stream
    print(f"\nConnecting to {stream_url}...")
    cap = cv2.VideoCapture(stream_url)
    
    if not cap.isOpened():
        print(f"\n❌ Error: Cannot connect to RemoteCam at {stream_url}")
        if not config.auto_detect:
            print("  Try using --auto-detect to find the correct IP")
        sys.exit(1)
            
    print("✅ Connected to stream!")
    
    # 5. Initialize Virtual Camera
    virtual_cam = None
    if PYVIRTUALCAM_AVAILABLE and not args.no_virtual_cam:
        try:
            virtual_cam = pyvirtualcam.Camera(
                width=config.width,
                height=config.height,
                fps=config.fps,
                fmt=pyvirtualcam.PixelFormat.RGB,
                device=config.virtual_camera_name if hasattr(config, 'virtual_camera_name') else None
            )
            print(f"🎥 Virtual camera started: {virtual_cam.device}")
        except Exception as e:
            print(f"⚠️  Could not start virtual camera: {e}")
            virtual_cam = None
            
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
            
            # Apply Filters (Rotation, etc.)
            if filters:
                frame = apply_filters(frame, filters)
                
            # --- Hand Tracking & Mouse Control ---
            if use_mouse_control and hand_tracker:
                # Process hand tracking
                hand_tracker.process(frame)
                
                # Get index finger position (normalized 0.0-1.0)
                pos = hand_tracker.get_pointer_position()
                
                if pos:
                    x, y = pos
                    
                    # Move Mouse (Flip X because camera is mirrored typically)
                    # Use a margin to reach edges easily (0.1 - 0.9 maps to 0.0 - 1.0)
                    margin = 0.1
                    mapped_x = (x - margin) / (1 - 2*margin)
                    mapped_y = (y - margin) / (1 - 2*margin)
                    
                    # Mirror X for natural feeling
                    mouse.move(1.0 - mapped_x, mapped_y)
                    
                    # Check for click (pinch)
                    if hand_tracker.is_pinching(threshold=0.04):
                        mouse.click()
                        cv2.circle(frame, (int(x*config.width), int(y*config.height)), 20, (0, 255, 0), cv2.FILLED)
                
                # Draw landmarks on frame for preview
                frame = hand_tracker.draw_landmarks(frame)
            # -------------------------------------
            
            # Calculate FPS
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                fps_display = frame_count / elapsed
                frame_count = 0
                start_time = time.time()
            
            # Send to Virtual Camera (BGR -> RGB)
            if virtual_cam is not None:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                virtual_cam.send(rgb_frame)
                virtual_cam.sleep_until_next_frame()
                
            # Preview Window
            if args.preview or virtual_cam is None:
                preview_frame = frame.copy()
                
                cv2.putText(preview_frame, f"FPS: {fps_display:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                if use_mouse_control:
                    cv2.putText(preview_frame, "MOUSE CONTROL ON", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                cv2.imshow("RemoteCam Enhanced", preview_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        cap.release()
        if virtual_cam:
            virtual_cam.close()
        cv2.destroyAllWindows()
        print("Done.")


if __name__ == "__main__":
    main()
