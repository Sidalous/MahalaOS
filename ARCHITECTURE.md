# Architecture

Technical overview of the software stack and how the pieces fit together.

---

## Stack Overview

```
┌─────────────────────────────────────────────┐
│              User-Facing Layer               │
│  Phosh (GNOME Mobile Shell)                  │
│  Native GTK Apps + Waydroid (Android Apps)   │
├─────────────────────────────────────────────┤
│              Middleware                       │
│  PipeWire (audio) · BlueZ (bluetooth)        │
│  ModemManager (cellular) · NetworkManager    │
│  libcamera (camera) · iio-sensor-proxy       │
├─────────────────────────────────────────────┤
│              Base OS                          │
│  postmarketOS (Alpine Linux)                 │
│  musl libc · OpenRC · apk package manager    │
├─────────────────────────────────────────────┤
│              Kernel                           │
│  Mainline Linux (with device-specific        │
│  patches for OnePlus 6T / Snapdragon 845)    │
├─────────────────────────────────────────────┤
│              Firmware (proprietary)           │
│  Qualcomm modem · Adreno GPU · Wi-Fi/BT      │
│  TrustZone · DSP                             │
└─────────────────────────────────────────────┘
```

## Key Components

### Phosh (UI Shell)
GNOME-based mobile shell. Handles the home screen, app launcher, notifications, quick settings, and lock screen. Written primarily in C with GObject. Upstream: https://gitlab.gnome.org/World/Phosh/phosh

### Waydroid (Android Compatibility)
Runs a full Android system inside a Linux container using LXC. Android apps render natively through Wayland — no emulation. This is how WhatsApp, Messenger, and other Android-only apps run on the device. Our work focuses on making the bridge between Waydroid and Phosh seamless — particularly notification forwarding and app switching.

### ModemManager (Cellular)
Manages the Qualcomm modem for calls, SMS, and data. Works with oFono as an alternative on some configurations. Telephony reliability depends heavily on this component and the proprietary modem firmware.

### PipeWire (Audio)
Handles all audio routing — call audio, media playback, Bluetooth audio. Replaced PulseAudio in most modern Linux configurations. Critical for call quality and Bluetooth headphone support.

### libcamera (Camera)
Camera capture framework. The OnePlus 6T uses Sony IMX376K (front) and Sony IMX519 (rear) sensors. Camera quality depends on both libcamera pipeline tuning and the proprietary Qualcomm ISP firmware.

## Device: OnePlus 6T (fajita)

| Component | Hardware | Linux Support |
|-----------|----------|---------------|
| SoC | Qualcomm Snapdragon 845 | Good — mainline kernel support |
| Modem | Snapdragon X20 LTE | Works via ModemManager (proprietary firmware) |
| Display | 6.41" AMOLED 1080x2340 | Working |
| GPU | Adreno 630 | Freedreno (open source driver) + proprietary firmware |
| Camera (rear) | Sony IMX519 16MP | Partial — needs tuning |
| Camera (front) | Sony IMX376K 16MP | Partial — needs tuning |
| Fingerprint | Synaptics in-display | Partial support |
| Wi-Fi/BT | Qualcomm WCN3990 | Working (proprietary firmware) |
| Storage | 128/256GB UFS 2.1 | Working |
| Battery | 3700 mAh | Working, power management needs tuning |

## Proprietary Firmware

The OnePlus 6T requires proprietary binary blobs for:
- Cellular modem operation
- GPU acceleration
- Wi-Fi and Bluetooth
- Camera ISP (image signal processing)
- TrustZone / secure enclave
- Audio DSP

These blobs run on separate processors within the SoC. The main application processor runs fully open source software. This is a pragmatic trade-off — see README for our rationale.

## Build System

[TBD — will be documented once established in Phase 0. Expected to be a set of shell scripts wrapping pmbootstrap (postmarketOS build tool) with our custom package list and configuration overlays.]

## Directory Structure

```
project-root/
├── README.md
├── GOOD_ENOUGH.md
├── ROADMAP.md
├── CONTRIBUTING.md
├── ARCHITECTURE.md
├── build/
│   ├── build-image.sh        # Main image build script
│   ├── configs/               # Device and OS configuration
│   └── packages/              # Custom package definitions
├── waydroid/
│   ├── setup.sh               # Automated Waydroid setup
│   └── notification-bridge/   # Bridge Waydroid notifications to Phosh
├── tweaks/
│   ├── power-management/      # Battery life optimisations
│   ├── camera/                # Camera tuning and config
│   ├── bluetooth/             # BT audio fixes
│   └── fingerprint/           # Fingerprint reader config
├── branding/
│   ├── wallpapers/
│   ├── boot-splash/
│   └── icons/
├── first-boot/
│   └── setup-wizard/          # First-boot configuration wizard
└── docs/
    ├── install-guide.md
    ├── testing-checklist.md
    └── known-issues.md
```
