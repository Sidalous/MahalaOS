#!/bin/bash
#
# flash-device.sh
# Flash the custom postmarketOS image to a connected OnePlus 6T.
#
# Prerequisites:
#   - OnePlus 6T connected via USB in fastboot mode
#   - OxygenOS 9.0.16 flashed with VoLTE enabled BEFORE running this
#   - Image built via build-image.sh
#
# Usage:
#   ./flash-device.sh
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

EXPORT_DIR="$(pwd)/output"

# =============================================================================
# PRE-FLIGHT CHECKS
# =============================================================================

echo ""
echo "=============================================="
echo "  OnePlus 6T Flash Tool"
echo "=============================================="
echo ""

# Check fastboot exists
if ! command -v fastboot &> /dev/null; then
    error "fastboot not found. Install: sudo apt install android-tools-adb android-tools-fastboot"
fi

# Check image files exist
if [ ! -f "$EXPORT_DIR/boot.img" ]; then
    error "boot.img not found in $EXPORT_DIR. Run build-image.sh first."
fi

# Check device is connected
info "Checking for connected device in fastboot mode..."
DEVICE_COUNT=$(fastboot devices | wc -l)

if [ "$DEVICE_COUNT" -eq 0 ]; then
    echo ""
    warn "No device found in fastboot mode."
    echo ""
    echo "To enter fastboot mode:"
    echo "  1. Power off the phone"
    echo "  2. Hold Volume Up + Power button"
    echo "  3. Release when you see the fastboot screen"
    echo ""
    echo "Then run this script again."
    exit 1
fi

info "Device detected!"
fastboot devices

# =============================================================================
# PRE-FLASH CHECKLIST
# =============================================================================

echo ""
echo "=============================================="
echo "  PRE-FLASH CHECKLIST"
echo "=============================================="
echo ""
echo "Before flashing, confirm the following:"
echo ""
echo "  [?] OxygenOS 9.0.16 was flashed to BOTH slots"
echo "  [?] You booted into Android and enabled VoLTE via engineering mode"
echo "  [?] You verified VoLTE calls worked in Android with your SIM"
echo "  [?] Bootloader is unlocked"
echo ""
read -p "Have you completed all the above steps? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo ""
    warn "Please complete the pre-flash checklist first."
    echo "See docs/install-guide.md for detailed instructions."
    exit 1
fi

# =============================================================================
# FLASH
# =============================================================================

echo ""
info "Starting flash process..."
echo ""
warn "THIS WILL ERASE ALL DATA ON THE PHONE"
read -p "Continue? (yes/no): " FLASH_CONFIRM

if [ "$FLASH_CONFIRM" != "yes" ]; then
    info "Flash cancelled."
    exit 0
fi

echo ""
info "Flashing boot image..."
fastboot flash boot "$EXPORT_DIR/boot.img"

info "Flashing root filesystem..."
fastboot flash userdata "$EXPORT_DIR/oneplus-fajita.img"

echo ""
info "Flash complete. Rebooting device..."
fastboot reboot

echo ""
echo "=============================================="
info "Done! Your phone should now boot into postmarketOS."
echo "=============================================="
echo ""
echo "First boot may take 1-2 minutes. Don't panic if it's slow."
echo ""
echo "Default login:"
echo "  Username: user"
echo "  Password: (whatever you set during build)"
echo ""
echo "If the phone doesn't boot:"
echo "  1. Hold Power for 10 seconds to force restart"
echo "  2. If stuck in a boot loop, enter fastboot mode and reflash"
echo "  3. Worst case, use MSMDownloadTool to restore OxygenOS"
echo ""
