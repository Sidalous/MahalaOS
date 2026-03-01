# MahalaOS Dev Log — Day 1 (26 Feb 2026)
### OnePlus 6T · Firmware conversion · VoLTE testing · Bootloader unlock

---

## Summary

Day 1 was about getting the hardware into a flashable state. The 6T arrived as a Chinese A6010 model, requiring firmware conversion to global before postmarketOS could be flashed. VoLTE was confirmed working on Vodafone UK before the bootloader was unlocked — important baseline data.

---

## Hardware Acquired

- **Device:** OnePlus 6T (A6010) — Chinese model, purchased second-hand for £73
- Required conversion from Chinese to global firmware before use

---

## Firmware Conversion

Used MSMDownloadTool to flash global firmware at work. Process worked but is not consumer-friendly — requires a Windows machine, specific drivers, and comfort with EDL mode.

This is a one-time step for the dev device, but worth noting for future documentation: any MahalaOS install guide will need to address the Chinese vs global firmware distinction clearly.

---

## VoLTE Confirmed (Pre-Flash Baseline)

Before unlocking the bootloader, confirmed VoLTE working on Vodafone UK while still on stock Android:

- Voice Network Type: LTE
- Test calls made — audio acceptable both directions
- This establishes a baseline: VoLTE hardware capability is present and working

**Why this matters:** VoLTE is a known pain point on postmarketOS. Confirming it works on stock Android before flashing means any VoLTE issues on pmOS are software/config rather than hardware.

---

## Bootloader Unlock

Unlocked the bootloader via `fastboot oem unlock`. Phone entered EDL mode unexpectedly — required recovery via MSMDownloadTool.

**Lesson learned:** Always have MSMDownloadTool and the firmware backup accessible before unlocking. Backed up to Google Drive for future use.

---

## Next Steps

- Flash postmarketOS
- Confirm VoLTE still working under pmOS
- Begin daily driving and friction point documentation
