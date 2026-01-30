#!/bin/bash
# =============================================================================
# RemoteCam - Setup v4l2loopback virtual webcam (Linux)
# =============================================================================
# This script installs and configures v4l2loopback to create a virtual webcam
# device that can receive video from RemoteCam
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  RemoteCam - v4l2loopback Setup${NC}"
echo -e "${GREEN}========================================${NC}"

# Configuration (can be overridden by environment variables)
VIDEO_NR=${VIDEO_NR:-10}
CARD_LABEL=${CARD_LABEL:-"RemoteCam Virtual Webcam"}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}Note: Some commands require sudo privileges${NC}"
fi

# Step 1: Install dependencies
echo -e "\n${GREEN}[1/4] Installing v4l2loopback and ffmpeg...${NC}"
sudo apt update
sudo apt install -y v4l2loopback-dkms v4l2loopback-utils ffmpeg v4l-utils

# Step 2: Load the kernel module
echo -e "\n${GREEN}[2/4] Loading v4l2loopback kernel module...${NC}"
sudo modprobe -r v4l2loopback 2>/dev/null || true
sudo modprobe v4l2loopback devices=1 video_nr=$VIDEO_NR card_label="$CARD_LABEL" exclusive_caps=1

# Step 3: Verify device creation
echo -e "\n${GREEN}[3/4] Verifying virtual device...${NC}"
if [ -e "/dev/video$VIDEO_NR" ]; then
    echo -e "${GREEN}✓ Virtual webcam created at /dev/video$VIDEO_NR${NC}"
else
    echo -e "${RED}✗ Failed to create virtual device${NC}"
    exit 1
fi

# Step 4: Display device info
echo -e "\n${GREEN}[4/4] Device information:${NC}"
v4l2-ctl --device=/dev/video$VIDEO_NR --info

# Make it persistent (optional)
echo -e "\n${YELLOW}To make v4l2loopback load on boot, run:${NC}"
echo "echo 'v4l2loopback' | sudo tee /etc/modules-load.d/v4l2loopback.conf"
echo "echo 'options v4l2loopback devices=1 video_nr=$VIDEO_NR card_label=\"$CARD_LABEL\" exclusive_caps=1' | sudo tee /etc/modprobe.d/v4l2loopback.conf"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup complete!${NC}"
echo -e "${GREEN}  Virtual webcam: /dev/video$VIDEO_NR${NC}"
echo -e "${GREEN}========================================${NC}"
