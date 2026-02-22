# Install Guide

Complete guide from unboxing to running postmarketOS on your OnePlus 6T.

---

## What You Need

- OnePlus 6T (128GB or 256GB, any colour, unlocked)
- USB-C cable
- Linux PC (Ubuntu 22.04+ recommended, or a VM)
- Windows PC or VM (for MSMDownloadTool in Step 1 only)
- A SIM card for testing calls

---

## Step 1: Flash OxygenOS 9.0.16 (Windows Required)

This step loads the correct modem firmware onto the phone. **Do not skip this** — VoLTE will not work without it.

1. Download the decrypted OxygenOS 9.0.16 repack for fajita from: https://www.thecustomdroid.com/oneplus-6-6t-unbrick-guide/
   - File: `fajita_41_O.23_190801_repack.zip`
   - This includes the MSMDownloadTool

2. Extract the zip on your Windows PC

3. Power off the phone completely

4. Hold **Volume Up + Volume Down** together, then plug in the USB cable
   - The screen should stay black — this is EDL (Emergency Download) mode
   - If Windows prompts for drivers, install the Qualcomm USB drivers included in the zip

5. Run `MsmDownloadTool V4.0.exe` as Administrator

6. The tool should detect your device. Click **Start**

7. Wait for the flash to complete (5-10 minutes). The phone will reboot into OxygenOS

**This flashes to both slots, giving you a completely clean starting point.**

---

## Step 2: Enable VoLTE in Android

Before leaving Android, you need to enable VoLTE in the modem firmware.

1. Complete the basic Android setup (skip Google account, just get to the home screen)

2. Install two APKs via ADB from your PC:
   - `EngineerMode.apk`
   - `OnePlusLogkit.apk`
   - (These can be found on XDA forums — search "OnePlus 6T engineer mode APK")

3. Open the phone dialler and enter: `*#800#`
   - Select to run with **Engineer Mode**

4. Open **OnePlus Logkit** from the app drawer
   - Go to **Feature Switch**
   - Toggle ON: **VoLTE**
   - Toggle ON: **VoWiFi** (optional but recommended)

5. Reboot the phone

6. Insert your SIM card

7. Make a test call — verify it connects and audio works both ways
   - Check the status bar shows a VoLTE icon
   - If no VoLTE icon appears, try toggling airplane mode on/off

**Do not proceed until you have confirmed VoLTE calls work in Android.**

---

## Step 3: Unlock the Bootloader

1. In Android, go to **Settings > About Phone**
2. Tap **Build Number** 7 times to enable Developer Options
3. Go to **Settings > Developer Options**
4. Enable **OEM Unlocking**
5. Reboot into fastboot mode:
   - Power off the phone
   - Hold **Volume Up + Power** until you see the fastboot screen
6. On your Linux PC:

```bash
fastboot oem unlock
```

7. Confirm on the phone (this will factory reset — that's expected)

---

## Step 4: Set Up Your Build Machine

On your Linux PC (or Ubuntu VM):

```bash
# Install pmbootstrap
pip3 install pmbootstrap

# Install flash tools
sudo apt install android-tools-adb android-tools-fastboot

# Clone the project repo
git clone https://github.com/YOUR-PROJECT/YOUR-PROJECT.git
cd YOUR-PROJECT
```

---

## Step 5: Build the Image

```bash
# Initialise pmbootstrap (first time only — will ask for a password for the image)
pmbootstrap init
# When prompted:
#   Channel: edge
#   Vendor: oneplus
#   Device: oneplus-fajita
#   UI: phosh

# Build the image with all packages
chmod +x build/build-image.sh
./build/build-image.sh
```

First build takes 15-30 minutes depending on your internet and CPU.

---

## Step 6: Flash postmarketOS

1. Boot the phone into fastboot mode:
   - Power off
   - Hold **Volume Up + Power**

2. Connect via USB

3. Flash:

```bash
chmod +x build/flash-device.sh
./build/flash-device.sh
```

Or manually:

```bash
fastboot flash boot output/boot.img
fastboot flash userdata output/oneplus-fajita.img
fastboot reboot
```

---

## Step 7: First Boot

- First boot may take 1-2 minutes — the screen may be black for a while, this is normal
- You'll see the Phosh lock screen
- Login with the password you set during `pmbootstrap init`
- Connect to Wi-Fi
- Insert your SIM if not already in

---

## Step 8: Set Up Waydroid (Android Apps)

After first boot, open a terminal (or SSH in from your PC):

```bash
# Initialise Waydroid
sudo waydroid init -s GAPPS

# Start the Waydroid container
sudo waydroid container start

# Launch the Waydroid session
waydroid session start
```

You can then install WhatsApp, Messenger, etc. via the Waydroid app store or by sideloading APKs.

---

## Troubleshooting

**Phone doesn't boot after flashing:**
- Hold Power for 10+ seconds to force restart
- If stuck in boot loop, enter fastboot mode and reflash
- Worst case, use MSMDownloadTool to restore OxygenOS and start over

**No cellular service:**
- Ensure SIM is in slot 1 (not slot 2)
- Only use one SIM — dual SIM is not fully supported
- Check ModemManager status: `mmcli -L`

**No sound on calls:**
- Check PipeWire is running: `systemctl --user status pipewire`
- Check WirePlumber: `systemctl --user status wireplumber`

**Waydroid won't start:**
- Ensure kernel modules are loaded: `modprobe binder_linux`
- Check logs: `waydroid log`

---

## Useful Commands

```bash
# Check modem status
mmcli -L
mmcli -m 0

# Check running services
systemctl --user status pipewire wireplumber

# View system logs
journalctl -b

# SSH into the phone from your PC
ssh user@PHONE_IP_ADDRESS

# Update all packages
sudo apk update && sudo apk upgrade
```
