#!/usr/bin/env python3
"""
=============================================================================
RemoteCam - Network Scanner Module
=============================================================================
Automatically detects phones running RemoteCam on the local network.
Scans the local subnet for devices responding on the RemoteCam port.
=============================================================================
"""

import socket
import urllib.request
import urllib.error
import concurrent.futures
from typing import List, Optional, Tuple
import ipaddress
import sys

# Force UTF-8 for stdout on Windows
if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def get_local_ip() -> str:
    """Get the local IP address of this machine."""
    try:
        # Create a socket to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "192.168.1.1"


def get_subnet(ip: str) -> str:
    """Get the /24 subnet from an IP address."""
    parts = ip.split('.')
    return f"{parts[0]}.{parts[1]}.{parts[2]}"


def check_remotecam(ip: str, port: int = 8080, timeout: float = 1.0) -> Optional[Tuple[str, int]]:
    """
    Check if a RemoteCam server is running at the given IP.
    
    Args:
        ip: IP address to check
        port: Port number (default: 8080)
        timeout: Connection timeout in seconds
        
    Returns:
        Tuple of (ip, port) if RemoteCam found, None otherwise
    """
    url = f"http://{ip}:{port}/video"
    try:
        request = urllib.request.Request(url, method='HEAD')
        response = urllib.request.urlopen(request, timeout=timeout)
        content_type = response.headers.get('Content-Type', '')
        
        # RemoteCam typically returns multipart/x-mixed-replace for MJPEG
        if 'multipart' in content_type or 'image' in content_type or 'video' in content_type:
            return (ip, port)
        
        # Also accept if we get a valid response (some implementations vary)
        if response.status == 200:
            return (ip, port)
            
    except (urllib.error.URLError, socket.timeout, ConnectionRefusedError, OSError):
        pass
    except Exception:
        pass
    
    return None


def scan_for_remotecam(
    subnet: Optional[str] = None,
    port: int = 8080,
    timeout: float = 1.0,
    max_workers: int = 50,
    progress_callback=None
) -> List[Tuple[str, int]]:
    """
    Scan the local network for RemoteCam servers.
    
    Args:
        subnet: Subnet to scan (e.g., "192.168.1"). If None, auto-detect.
        port: Port to check (default: 8080)
        timeout: Timeout per connection attempt
        max_workers: Number of parallel scan threads
        progress_callback: Optional callback(current, total) for progress updates
        
    Returns:
        List of (ip, port) tuples for found RemoteCam servers
    """
    if subnet is None:
        local_ip = get_local_ip()
        subnet = get_subnet(local_ip)
    
    # Generate IP list for the subnet (1-254)
    ips_to_scan = [f"{subnet}.{i}" for i in range(1, 255)]
    found_servers = []
    
    print(f"🔍 Scanning network {subnet}.0/24 for RemoteCam...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all scan jobs
        future_to_ip = {
            executor.submit(check_remotecam, ip, port, timeout): ip 
            for ip in ips_to_scan
        }
        
        completed = 0
        total = len(ips_to_scan)
        
        for future in concurrent.futures.as_completed(future_to_ip):
            completed += 1
            if progress_callback:
                progress_callback(completed, total)
            
            result = future.result()
            if result:
                found_servers.append(result)
                print(f"✅ Found RemoteCam at {result[0]}:{result[1]}")
    
    return found_servers


def find_remotecam(
    port: int = 8080,
    timeout: float = 1.0,
    prefer_ip: Optional[str] = None
) -> Optional[Tuple[str, int]]:
    """
    Find a single RemoteCam server on the network.
    
    Args:
        port: Port to check
        timeout: Timeout per connection
        prefer_ip: If specified, try this IP first before scanning
        
    Returns:
        Tuple of (ip, port) for the first found server, or None
    """
    # Try preferred IP first if specified
    if prefer_ip:
        result = check_remotecam(prefer_ip, port, timeout)
        if result:
            return result
        print(f"⚠️  RemoteCam not found at {prefer_ip}:{port}, scanning network...")
    
    # Scan the network
    servers = scan_for_remotecam(port=port, timeout=timeout)
    
    if servers:
        return servers[0]
    
    return None


def print_scan_progress(current: int, total: int):
    """Print a simple progress bar."""
    percent = (current / total) * 100
    bar_length = 30
    filled = int(bar_length * current / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"\r  Progress: [{bar}] {percent:.0f}%", end='', flush=True)
    if current == total:
        print()  # New line at end


if __name__ == "__main__":
    # Test the scanner
    print("=" * 50)
    print("  RemoteCam Network Scanner")
    print("=" * 50)
    print(f"  Local IP: {get_local_ip()}")
    print("=" * 50)
    
    servers = scan_for_remotecam(progress_callback=print_scan_progress)
    
    print()
    if servers:
        print(f"Found {len(servers)} RemoteCam server(s):")
        for ip, port in servers:
            print(f"  - http://{ip}:{port}/video")
    else:
        print("No RemoteCam servers found on the network.")
        print("Make sure:")
        print("  1. RemoteCam is running on your phone")
        print("  2. Phone and PC are on the same WiFi network")
