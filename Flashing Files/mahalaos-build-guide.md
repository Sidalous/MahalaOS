# MahalaOS Build Image Guide

## Overview

MahalaOS is a consumer-focused layer on top of postmarketOS. Rather than forking, we use **pmbootstrap** to build a standard postmarketOS image, then apply a **MahalaOS overlay** — a set of scripts, configs, and systemd services that fix the rough edges and make things work out of the box.

The build process:
1. **pmbootstrap** builds the base postmarketOS image (kernel, rootfs, packages)
2. **MahalaOS overlay** is injected into the image (firewall rules, Waydroid setup, first-boot wizard, etc.)
3. The final image is flashable via fastboot — user downloads, flashes, boots, done.

---

## Part 1: Setting Up pmbootstrap

### Prerequisites

You need a Linux machine (x86_64 or aarch64). Your Fedora machine works. **WSL does not work.**

```bash
# Install pmbootstrap (Fedora)
pip install --user pmbootstrap

# Or from git for latest
git clone https://gitlab.postmarketOS.org/postmarketOS/pmbootstrap.git
cd pmbootstrap
pip install --user .
```

Verify:
```bash
pmbootstrap --version
```

### Initialise for OnePlus 6T

```bash
pmbootstrap init
```

You'll be prompted for settings. Choose:

| Setting | Value |
|---------|-------|
| Channel | edge |
| Vendor | oneplus |
| Device | fajita (OnePlus 6T) |
| UI | gnome-mobile |
| Extra packages | (leave blank for now) |
| Username | user |
| Locale | en_GB.UTF-8 |
| Timezone | Europe/London |

This creates `~/.config/pmbootstrap.cfg` and clones the `pmaports` repository.

### Build the Base Image

```bash
# Build and install (creates the rootfs image)
pmbootstrap install

# Export the flashable images
pmbootstrap export
```

This creates symlinks in `/tmp/postmarketOS-export/`:
- `oneplus-fajita-boot.img` — kernel + initramfs
- `oneplus-fajita.img` — root filesystem

### Flash to Device

With the phone in fastboot mode (unlocked bootloader):

```bash
# Flash boot partition
pmbootstrap flasher flash_kernel

# Flash system/userdata partition
pmbootstrap flasher flash_rootfs
```

Or manually:
```bash
cd /tmp/postmarketOS-export/
sudo fastboot flash boot oneplus-fajita-boot.img
sudo fastboot flash userdata oneplus-fajita.img
sudo fastboot reboot
```

---

## Part 2: The MahalaOS Overlay

This is where MahalaOS adds value. The overlay is a directory structure that mirrors the rootfs and gets copied into the image before flashing.

### Directory Structure

```
mahalaos/
├── overlay/
│   ├── etc/
│   │   ├── systemd/system/
│   │   │   ├── mahala-waydroid-net.service
│   │   │   ├── mahala-waydroid-init.service
│   │   │   └── mahala-first-boot.service
│   │   └── nftables.d/
│   │       └── mahala-waydroid.nft
│   ├── usr/
│   │   └── local/
│   │       └── bin/
│   │           ├── mahala-waydroid-setup.sh
│   │           └── mahala-first-boot.sh
│   └── home/
│       └── user/
│           └── .config/
│               └── (default app configs)
├── build.sh              # Master build script
├── inject-overlay.sh     # Injects overlay into pmbootstrap image
└── README.md
```

### Fix 1: Waydroid Firewall (Found Today)

**Problem:** postmarketOS nftables firewall blocks Waydroid DHCP and forwarding.
**Fix:** Add nftables rules allowing waydroid0 traffic.

**`overlay/etc/systemd/system/mahala-waydroid-net.service`**
```ini
[Unit]
Description=MahalaOS Waydroid firewall rules
After=network.target nftables.service
Before=waydroid-container.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/nft add rule inet filter input iifname "waydroid0" accept
ExecStart=/usr/sbin/nft add rule inet filter forward iifname "waydroid0" accept
ExecStart=/usr/sbin/nft add rule inet filter forward oifname "waydroid0" ct state established,related accept

[Install]
WantedBy=multi-user.target
```

### Fix 2: Waydroid Auto-Initialisation

**Problem:** User must manually run `sudo waydroid init -s GAPPS` from terminal.
**Fix:** First-boot service handles it.

**`overlay/usr/local/bin/mahala-waydroid-setup.sh`**
```bash
#!/bin/bash
# MahalaOS Waydroid Setup
# Runs on first boot to initialise Waydroid with GAPPS

MARKER="/var/lib/mahala/.waydroid-initialized"

if [ -f "$MARKER" ]; then
    echo "Waydroid already initialized"
    exit 0
fi

echo "MahalaOS: Initializing Waydroid with Google Apps..."

# Initialize with GAPPS
waydroid init -s GAPPS

# Create marker
mkdir -p /var/lib/mahala
touch "$MARKER"

echo "MahalaOS: Waydroid initialization complete"
```

**`overlay/etc/systemd/system/mahala-waydroid-init.service`**
```ini
[Unit]
Description=MahalaOS Waydroid first-time initialization
After=network-online.target
Wants=network-online.target
ConditionPathExists=!/var/lib/mahala/.waydroid-initialized

[Service]
Type=oneshot
ExecStart=/usr/local/bin/mahala-waydroid-setup.sh
TimeoutStartSec=600

[Install]
WantedBy=multi-user.target
```

### Fix 3: SSH Enabled for Dev Builds

**Problem:** Web flasher images don't enable SSH.
**Fix:** Enable SSH by default in dev builds, disable in consumer builds.

Handled in the build script with a `--dev` flag.

### Fix 4: VoLTE Auto-Enable

**Problem:** VoLTE service (81voltd) must be manually installed and enabled.
**Fix:** Include in package list and enable the service.

Added to the pmbootstrap extra packages and enabled via overlay.

---

## Part 3: The Build Script

**`build.sh`**
```bash
#!/bin/bash
set -e

# MahalaOS Build Script
# Usage: ./build.sh [--dev] [--no-waydroid]

DEV_BUILD=false
INCLUDE_WAYDROID=true
DEVICE="oneplus-fajita"
UI="gnome-mobile"
CHANNEL="edge"

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev) DEV_BUILD=true; shift ;;
        --no-waydroid) INCLUDE_WAYDROID=false; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "========================================="
echo "  MahalaOS Build"
echo "  Device: $DEVICE"
echo "  UI: $UI"
echo "  Channel: $CHANNEL"
echo "  Dev build: $DEV_BUILD"
echo "  Waydroid: $INCLUDE_WAYDROID"
echo "========================================="

# Step 1: Configure pmbootstrap
echo "[1/5] Configuring pmbootstrap..."

# Extra packages to install
EXTRA_PKGS="81voltd modemmanager"

if [ "$INCLUDE_WAYDROID" = true ]; then
    EXTRA_PKGS="$EXTRA_PKGS waydroid"
fi

if [ "$DEV_BUILD" = true ]; then
    EXTRA_PKGS="$EXTRA_PKGS openssh htop nano"
fi

# Step 2: Build the image
echo "[2/5] Building postmarketOS image..."
pmbootstrap install --no-fde

# Step 3: Install extra packages into the chroot
echo "[3/5] Installing extra packages..."
for pkg in $EXTRA_PKGS; do
    pmbootstrap chroot -- apk add "$pkg"
done

# Step 4: Inject MahalaOS overlay
echo "[4/5] Injecting MahalaOS overlay..."
./inject-overlay.sh "$DEV_BUILD"

# Step 5: Export
echo "[5/5] Exporting flashable images..."
pmbootstrap export

echo ""
echo "========================================="
echo "  Build complete!"
echo "  Images at: /tmp/postmarketOS-export/"
echo "========================================="
echo ""
echo "Flash with:"
echo "  sudo fastboot flash boot /tmp/postmarketOS-export/${DEVICE}-boot.img"
echo "  sudo fastboot flash userdata /tmp/postmarketOS-export/${DEVICE}.img"
echo "  sudo fastboot reboot"
```

**`inject-overlay.sh`**
```bash
#!/bin/bash
set -e

# Inject MahalaOS overlay into the pmbootstrap rootfs chroot
DEV_BUILD=${1:-false}
OVERLAY_DIR="$(dirname "$0")/overlay"

echo "Injecting MahalaOS overlay..."

# Copy overlay files into chroot
pmbootstrap chroot -- mkdir -p /var/lib/mahala

# Copy systemd services
for service in overlay/etc/systemd/system/*.service; do
    filename=$(basename "$service")
    cat "$service" | pmbootstrap chroot -- tee "/etc/systemd/system/$filename" > /dev/null
    pmbootstrap chroot -- systemctl enable "$filename"
done

# Copy scripts
for script in overlay/usr/local/bin/*.sh; do
    filename=$(basename "$script")
    cat "$script" | pmbootstrap chroot -- tee "/usr/local/bin/$filename" > /dev/null
    pmbootstrap chroot -- chmod +x "/usr/local/bin/$filename"
done

# Enable VoLTE
pmbootstrap chroot -- systemctl enable 81voltd

# Enable SSH for dev builds only
if [ "$DEV_BUILD" = true ]; then
    pmbootstrap chroot -- systemctl enable sshd
    echo "SSH enabled (dev build)"
else
    pmbootstrap chroot -- systemctl disable sshd 2>/dev/null || true
    echo "SSH disabled (consumer build)"
fi

echo "Overlay injection complete"
```

---

## Part 4: Applying Fixes to Your Current Device (Right Now)

You don't need to rebuild the image to test fixes. Apply them directly to the running phone:

### Make the Waydroid firewall fix permanent

```bash
# SSH into the phone
ssh user@172.16.42.1

# Create the service file
sudo tee /etc/systemd/system/mahala-waydroid-net.service << 'EOF'
[Unit]
Description=MahalaOS Waydroid firewall rules
After=network.target nftables.service
Before=waydroid-container.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/nft add rule inet filter input iifname "waydroid0" accept
ExecStart=/usr/sbin/nft add rule inet filter forward iifname "waydroid0" accept

[Install]
WantedBy=multi-user.target
EOF

# Enable it
sudo systemctl enable mahala-waydroid-net.service

# Reboot and verify Waydroid gets internet automatically
sudo reboot
```

### After reboot, verify

```bash
# Check the service ran
sudo systemctl status mahala-waydroid-net

# Check Waydroid has an IP
waydroid status

# Open browser in Waydroid — should have internet
```

---

## Part 5: Iterative Improvement Workflow

This is how you'll work going forward:

1. **Find a problem** on the phone (e.g., "Waydroid has no internet")
2. **Fix it manually** on the device via SSH
3. **Document the fix** — what file changed, what command ran
4. **Add it to the overlay** — create the service/config/script
5. **Test the overlay** by running `inject-overlay.sh` on a fresh build
6. **Commit to git** — push to github.com/Sidalous/MahalaOS
7. **Repeat**

Every fix makes the next user's experience better. Every fix is evidence for your NLnet application.

---

## Fixes Found Today (28 Feb 2026)

| # | Problem | Root Cause | Fix | Status |
|---|---------|-----------|-----|--------|
| 1 | Waydroid no internet | nftables `inet filter` blocks waydroid0 DHCP + forwarding | `nft add rule inet filter input iifname "waydroid0" accept` + forward rule | ✅ Fixed |
| 2 | SSH not available | Web flasher doesn't enable sshd | `systemctl enable sshd` (dev builds only) | ✅ Fixed |
| 3 | Call audio echo | PipeWire echo cancellation not configured | Needs telephony contributor | ⏳ Pending |
| 4 | Waydroid needs manual init | No auto-setup for GAPPS | First-boot service script | 📋 Designed |
| 5 | No first-boot wizard | User dropped into raw desktop | Needs MahalaOS welcome app | 📋 Planned |

---

## Next Steps

1. **Today:** Apply the firewall fix permanently on the 6T, verify Waydroid works after reboot
2. **This week:** Set up pmbootstrap on Fedora, build first custom image
3. **This week:** Create the GitHub repo structure with overlay directory
4. **Week 2:** Build and flash a MahalaOS image, verify all fixes work from clean flash
5. **Week 3:** Add more fixes from ongoing testing, automate the build
6. **Month 2:** CI pipeline that builds nightly images
7. **Month 3:** NLnet application with working demo image
