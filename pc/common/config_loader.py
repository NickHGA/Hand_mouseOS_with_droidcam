#!/usr/bin/env python3
"""
=============================================================================
RemoteCam - Configuration Loader Module
=============================================================================
Loads and merges configuration from config.yaml file with CLI arguments.
CLI arguments take priority over config file values.
=============================================================================
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

# Try to import PyYAML, fall back to basic parsing if not available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class RemoteCamConfig:
    """Configuration container for RemoteCam settings."""
    # RemoteCam connection
    phone_ip: str = "192.168.1.100"
    port: int = 8080
    endpoint: str = "/video"
    
    # Video settings
    width: int = 640
    height: int = 480
    fps: int = 30
    pixel_format: str = "yuyv422"
    
    # Linux specific
    video_device: str = "/dev/video10"
    device_label: str = "RemoteCam Virtual Webcam"
    
    # Windows specific
    virtual_camera_name: str = "OBS Virtual Camera"
    
    # Network scanning
    auto_detect: bool = False
    scan_timeout: float = 1.0
    
    # Filters
    filters: list = field(default_factory=list)
    rotate: int = 0
    brightness: int = 0
    contrast: int = 0
    blur: int = 0
    
    # Display
    preview: bool = False
    flip: str = "none"
    
    def get_stream_url(self) -> str:
        """Build the full stream URL."""
        return f"http://{self.phone_ip}:{self.port}{self.endpoint}"


def find_config_file() -> Optional[Path]:
    """Find the config.yaml file in common locations."""
    # Check various locations
    search_paths = [
        Path(__file__).parent / "config.yaml",  # Same directory as this module
        Path.cwd() / "config.yaml",  # Current working directory
        Path.cwd() / "common" / "config.yaml",  # common subdirectory
        Path.cwd() / "pc" / "common" / "config.yaml",  # pc/common subdirectory
    ]
    
    for path in search_paths:
        if path.exists():
            return path
    
    return None


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    if not YAML_AVAILABLE:
        print("Warning: PyYAML not installed. Using default configuration.")
        print("Install with: pip install pyyaml")
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config if config else {}
    except Exception as e:
        print(f"Warning: Could not load config file: {e}")
        return {}


def load_config(
    config_path: Optional[str] = None,
    cli_args: Optional[Dict[str, Any]] = None
) -> RemoteCamConfig:
    """
    Load configuration from file and merge with CLI arguments.
    
    Priority (highest to lowest):
    1. CLI arguments
    2. Config file values
    3. Default values
    
    Args:
        config_path: Optional path to config.yaml
        cli_args: Optional dictionary of CLI arguments
        
    Returns:
        RemoteCamConfig object with merged configuration
    """
    config = RemoteCamConfig()
    
    # Find and load config file
    if config_path:
        path = Path(config_path)
    else:
        path = find_config_file()
    
    if path and path.exists():
        yaml_config = load_yaml_config(path)
        
        # Apply YAML config values
        if 'remotecam' in yaml_config:
            rc = yaml_config['remotecam']
            if 'phone_ip' in rc:
                config.phone_ip = rc['phone_ip']
            if 'port' in rc:
                config.port = rc['port']
            if 'endpoint' in rc:
                config.endpoint = rc['endpoint']
        
        if 'video' in yaml_config:
            v = yaml_config['video']
            if 'width' in v:
                config.width = v['width']
            if 'height' in v:
                config.height = v['height']
            if 'fps' in v:
                config.fps = v['fps']
            if 'pixel_format' in v:
                config.pixel_format = v['pixel_format']
        
        if 'linux' in yaml_config:
            l = yaml_config['linux']
            if 'video_device_number' in l:
                config.video_device = f"/dev/video{l['video_device_number']}"
            if 'device_label' in l:
                config.device_label = l['device_label']
        
        if 'windows' in yaml_config:
            w = yaml_config['windows']
            if 'virtual_camera_name' in w:
                config.virtual_camera_name = w['virtual_camera_name']
        
        if 'network' in yaml_config:
            n = yaml_config['network']
            if 'auto_detect' in n:
                config.auto_detect = n['auto_detect']
            if 'scan_timeout' in n:
                config.scan_timeout = n['scan_timeout']
        
        if 'filters' in yaml_config:
            f = yaml_config['filters']
            if 'enabled' in f:
                config.filters = f['enabled']
            if 'rotate' in f:
                config.rotate = f['rotate']
            if 'brightness' in f:
                config.brightness = f['brightness']
            if 'contrast' in f:
                config.contrast = f['contrast']
            if 'blur' in f:
                config.blur = f['blur']
    
    # Apply CLI arguments (highest priority)
    if cli_args:
        for key, value in cli_args.items():
            if value is not None and hasattr(config, key):
                setattr(config, key, value)
        
        # Handle special CLI mappings
        if cli_args.get('ip'):
            config.phone_ip = cli_args['ip']
        if cli_args.get('device'):
            config.video_device = cli_args['device']
        if cli_args.get('auto_detect'):
            config.auto_detect = True
    
    return config


def get_stream_url(config: Optional[RemoteCamConfig] = None) -> str:
    """Get the RemoteCam stream URL from config or defaults."""
    if config is None:
        config = load_config()
    return config.get_stream_url()


if __name__ == "__main__":
    # Test the config loader
    print("=" * 50)
    print("  RemoteCam Config Loader Test")
    print("=" * 50)
    
    config = load_config()
    
    print(f"  Phone IP:      {config.phone_ip}")
    print(f"  Port:          {config.port}")
    print(f"  Stream URL:    {config.get_stream_url()}")
    print(f"  Resolution:    {config.width}x{config.height}")
    print(f"  FPS:           {config.fps}")
    print(f"  Auto-detect:   {config.auto_detect}")
    print(f"  Filters:       {config.filters}")
    print("=" * 50)
