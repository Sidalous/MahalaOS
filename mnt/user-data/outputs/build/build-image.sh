#!/bin/bash
# =============================================================================
# [PROJECT NAME] - Build Script
# Builds a custom postmarketOS image for OnePlus 6T (fajita)
# =============================================================================
#
# PREREQUISITES:
#   1. Linux host (Ubuntu 22.04+ recommended)
#   2. pmbootstrap installed: pip3 install pmbootstrap
#   3. OxygenOS 9.0.16 already flashed to the device (both slots)
#   4. VoLTE enabled via engineering mode in Android BEFORE flashing this image
#
# USAGE:
#   chmod +x build-image.sh
#   ./build-image.sh
#
# The script will produce a flashable image in the output directory.
# =============================================================================

set -e  # Exit on any error

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
PROJECT_NAME="[project-name]"
DEVICE="oneplus-fajita"
VENDOR="oneplus"
UI="phosh"
CHANNEL="edge"
WORK_DIR="$HOME/.local/var/pmbootstrap"
OUTPUT_DIR="$(pwd)/output"
IMAGE_DATE=$(date +%Y%m%d)

# Default user credentials (user should change on first boot)
DEFAULT_USER="user"

# -----------------------------------------------------------------------------
# Colours for output
# -----------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Colour

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# -----------------------------------------------------------------------------
# Pre-flight checks
# -----------------------------------------------------------------------------
log_info "Starting ${PROJECT_NAME} image build..."
echo ""

# Check pmbootstrap is installed
if ! command -v pmbootstrap &> /dev/null; then
    log_error "pmbootstrap not found. Install it with: pip3 install pmbootstrap"
    exit 1
fi

# Check running as non-root (pmbootstrap doesn't like root)
if [ "$EUID" -eq 0 ]; then
    log_error "Do not run this script as root. pmbootstrap handles sudo internally."
    exit 1
fi

log_info "All pre-flight checks passed."
echo ""

# -----------------------------------------------------------------------------
# Package lists
# -----------------------------------------------------------------------------

# Core telephony - calls, SMS, mobile data
TELEPHONY_PACKAGES=(
    "81voltd"               # VoLTE on Snapdragon 845 - ESSENTIAL for UK carriers
    "modemmanager"          # Cellular modem management
    "calls"                 # GNOME Calls - dialler app
    "chatty"                # SMS/MMS messaging
)

# Audio stack
AUDIO_PACKAGES=(
    "pipewire"              # Modern audio routing
    "wireplumber"           # Audio session manager - auto-switches profiles for calls
)

# Android app compatibility
ANDROID_PACKAGES=(
    "waydroid"              # Android container - runs WhatsApp, Messenger etc
)

# Networking
NETWORK_PACKAGES=(
    "networkmanager"        # Wi-Fi, mobile data, VPN management
    "bluez"                 # Bluetooth stack
    "wpa-supplicant"        # Wi-Fi authentication
)

# Browser
BROWSER_PACKAGES=(
    "firefox"               # Primary web browser + fallback for web banking
)

# Navigation
NAV_PACKAGES=(
    "pure-maps"             # Turn-by-turn navigation with OpenStreetMap
    "geoclue"               # Location services framework
)

# Camera
CAMERA_PACKAGES=(
    "megapixels"            # Camera app for Linux phones
    "libcamera"             # Camera framework for Sony IMX519/376K sensors
)

# GNOME apps - everyday essentials
GNOME_PACKAGES=(
    "gnome-text-editor"     # Notes
    "nautilus"              # File manager
    "gnome-calculator"      # Calculator
    "gnome-clocks"          # Alarms, timers, world clock
    "gnome-calendar"        # Calendar
    "gnome-contacts"        # Contact management
    "gnome-weather"         # Weather
)

# System - UI shell and core services
SYSTEM_PACKAGES=(
    "phosh"                 # Mobile shell - home screen, notifications, lock screen
    "squeekboard"           # On-screen keyboard
    "feedbackd"             # Haptic feedback and vibration
    "iio-sensor-proxy"      # Accelerometer/gyro - enables auto-rotation
    "power-profiles-daemon" # Power management for battery life
    "gnome-settings-daemon" # System settings backend
)

# Combine all packages into a comma-separated string
ALL_PACKAGES=(
    "${TELEPHONY_PACKAGES[@]}"
    "${AUDIO_PACKAGES[@]}"
    "${ANDROID_PACKAGES[@]}"
    "${NETWORK_PACKAGES[@]}"
    "${BROWSER_PACKAGES[@]}"
    "${NAV_PACKAGES[@]}"
    "${CAMERA_PACKAGES[@]}"
    "${GNOME_PACKAGES[@]}"
    "${SYSTEM_PACKAGES[@]}"
)

PACKAGE_STRING=$(IFS=,; echo "${ALL_PACKAGES[*]}")

# -----------------------------------------------------------------------------
# Initialise pmbootstrap
# -----------------------------------------------------------------------------
log_info "Configuring pmbootstrap for ${DEVICE}..."

# Set pmbootstrap config non-interactively
pmbootstrap config channel "${CHANNEL}"
pmbootstrap config device "${DEVICE}"
pmbootstrap config ui "${UI}"
pmbootstrap config extra_packages "${PACKAGE_STRING}"
pmbootstrap config user "${DEFAULT_USER}"
pmbootstrap config locale "en_GB.UTF-8"
pmbootstrap config timezone "Europe/London"

log_info "pmbootstrap configured."
echo ""

# -----------------------------------------------------------------------------
# Build the image
# -----------------------------------------------------------------------------
log_info "Building image with the following packages:"
echo ""
log_info "  Telephony:  ${TELEPHONY_PACKAGES[*]}"
log_info "  Audio:      ${AUDIO_PACKAGES[*]}"
log_info "  Android:    ${ANDROID_PACKAGES[*]}"
log_info "  Network:    ${NETWORK_PACKAGES[*]}"
log_info "  Browser:    ${BROWSER_PACKAGES[*]}"
log_info "  Navigation: ${NAV_PACKAGES[*]}"
log_info "  Camera:     ${CAMERA_PACKAGES[*]}"
log_info "  GNOME Apps: ${GNOME_PACKAGES[*]}"
log_info "  System:     ${SYSTEM_PACKAGES[*]}"
echo ""

log_info "This will take a while. Go make a brew."
echo ""

# Build the image
# --add flag ensures our extra packages are included
pmbootstrap install --add="${PACKAGE_STRING}"

log_info "Image built successfully."
echo ""

# -----------------------------------------------------------------------------
# Export the image
# -----------------------------------------------------------------------------
log_info "Exporting image..."

mkdir -p "${OUTPUT_DIR}"
pmbootstrap export "${OUTPUT_DIR}"

log_info "Image exported to ${OUTPUT_DIR}/"
echo ""

# -----------------------------------------------------------------------------
# Generate checksums
# -----------------------------------------------------------------------------
log_info "Generating SHA256 checksums..."

cd "${OUTPUT_DIR}"
sha256sum *.img > "${PROJECT_NAME}-${IMAGE_DATE}-SHA256SUMS.txt" 2>/dev/null || true
cd - > /dev/null

log_info "Checksums saved to ${OUTPUT_DIR}/${PROJECT_NAME}-${IMAGE_DATE}-SHA256SUMS.txt"
echo ""

# -----------------------------------------------------------------------------
# Done
# -----------------------------------------------------------------------------
echo ""
echo "============================================================================="
log_info "BUILD COMPLETE"
echo "============================================================================="
echo ""
log_info "Output files are in: ${OUTPUT_DIR}/"
echo ""
log_info "To flash to your OnePlus 6T:"
echo ""
echo "  1. Connect phone via USB"
echo "  2. Reboot to fastboot:  adb reboot bootloader"
echo "  3. Flash rootfs:        pmbootstrap flasher flash_rootfs"
echo "  4. Flash kernel:        pmbootstrap flasher flash_kernel"
echo "  5. Reboot:              fastboot reboot"
echo ""
log_info "Default login: user / (password you set during build)"
echo ""
log_warn "REMINDER: OxygenOS 9.0.16 must have been flashed FIRST with VoLTE"
log_warn "enabled via engineering mode. If you skipped this, calls will not work."
echo ""
echo "============================================================================="
