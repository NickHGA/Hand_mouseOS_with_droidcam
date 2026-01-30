#!/bin/bash
# =============================================================================
# RemoteCam - Stream to Virtual Webcam (Linux)
# =============================================================================
# This script captures the MJPEG stream from RemoteCam and pipes it to the
# virtual webcam device created by v4l2loopback
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Default configuration
PHONE_IP="${PHONE_IP:-192.168.1.100}"
PHONE_PORT="${PHONE_PORT:-8080}"
STREAM_ENDPOINT="${STREAM_ENDPOINT:-/video}"
VIDEO_DEVICE="${VIDEO_DEVICE:-/dev/video10}"
WIDTH="${WIDTH:-640}"
HEIGHT="${HEIGHT:-480}"
FPS="${FPS:-30}"
PIX_FMT="${PIX_FMT:-yuyv422}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--ip)
            PHONE_IP="$2"
            shift 2
            ;;
        -p|--port)
            PHONE_PORT="$2"
            shift 2
            ;;
        -d|--device)
            VIDEO_DEVICE="$2"
            shift 2
            ;;
        -r|--resolution)
            IFS='x' read -r WIDTH HEIGHT <<< "$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -i, --ip IP          Phone IP address (default: 192.168.1.100)"
            echo "  -p, --port PORT      RemoteCam port (default: 8080)"
            echo "  -d, --device DEV     Video device (default: /dev/video10)"
            echo "  -r, --resolution RES Resolution WxH (default: 640x480)"
            echo "  -h, --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build the stream URL
STREAM_URL="http://${PHONE_IP}:${PHONE_PORT}${STREAM_ENDPOINT}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  RemoteCam to Virtual Webcam${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${CYAN}Stream URL:${NC}    $STREAM_URL"
echo -e "${CYAN}Video Device:${NC}  $VIDEO_DEVICE"
echo -e "${CYAN}Resolution:${NC}    ${WIDTH}x${HEIGHT}"
echo -e "${CYAN}Framerate:${NC}     ${FPS} fps"
echo -e "${GREEN}========================================${NC}"

# Check if video device exists
if [ ! -e "$VIDEO_DEVICE" ]; then
    echo -e "${RED}Error: Video device $VIDEO_DEVICE does not exist${NC}"
    echo -e "${YELLOW}Run setup_v4l2loopback.sh first to create the virtual device${NC}"
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}Error: ffmpeg is not installed${NC}"
    echo -e "${YELLOW}Install it with: sudo apt install ffmpeg${NC}"
    exit 1
fi

# Test connection to RemoteCam
echo -e "\n${YELLOW}Testing connection to RemoteCam...${NC}"
if curl --connect-timeout 5 -s -o /dev/null "$STREAM_URL"; then
    echo -e "${GREEN}✓ RemoteCam is reachable${NC}"
else
    echo -e "${RED}✗ Cannot reach RemoteCam at $STREAM_URL${NC}"
    echo -e "${YELLOW}Make sure:${NC}"
    echo "  1. RemoteCam is running on your phone"
    echo "  2. Phone and PC are on the same network"
    echo "  3. IP address is correct ($PHONE_IP)"
    exit 1
fi

# Start streaming
echo -e "\n${GREEN}Starting stream... (Press Ctrl+C to stop)${NC}\n"

ffmpeg \
    -f mjpeg \
    -i "$STREAM_URL" \
    -vf "scale=${WIDTH}:${HEIGHT}" \
    -pix_fmt "$PIX_FMT" \
    -f v4l2 \
    -r "$FPS" \
    "$VIDEO_DEVICE"
