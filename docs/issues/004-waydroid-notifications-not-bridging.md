# Issue 004 — Waydroid notifications not bridging to GNOME host OS

**Date:** 02/03/2026
**Device:** OnePlus 6T (fajita), postmarketOS edge, GNOME Mobile
**Severity:** Major
**Status:** Open / Upstream

---

## Summary

WhatsApp running inside Waydroid does not surface notifications to the GNOME host OS. The phone gives no notification, vibration, or sound when a WhatsApp message is received while the app is in the background or the phone is locked. Messages only deliver when the app is foregrounded manually.

---

## Steps to Reproduce

1. Install WhatsApp inside Waydroid
2. Lock the phone or leave WhatsApp in the background
3. Send a WhatsApp message to the device from another phone
4. Observe: no notification, no sound, no vibration
5. Open WhatsApp manually — messages appear, read receipts send, and the one-time fluke notification may appear

## Expected

WhatsApp messages received while the phone is locked or the app is backgrounded surface as a native GNOME notification — sound, vibration, and lock screen notification — identical to a native app.

## Actual

No notification of any kind. Messages only appear when WhatsApp is opened manually. Read receipts are inconsistent — sometimes sending immediately, sometimes delayed until the app is foregrounded.

---

## Investigation

### Waydroid container freezes when backgrounded

`waydroid status` shows:

```
Session:    RUNNING
Container:  FROZEN
IP address: UNKNOWN
```

When the container is frozen, Android is paused and has no network access. FCM (Firebase Cloud Messaging) pushes cannot be received. WhatsApp only syncs when the container unfreezes — i.e. when the app is foregrounded.

### Session running doesn't fix it

Running `waydroid session start` to keep the session active and unforzen did not resolve the issue. Messages still only delivered when the app was opened manually. This indicates the problem is deeper than the freeze/thaw cycle.

### FCM/GMS not maintaining persistent connection

Even with the session running, Google Play Services (`com.google.android.gms`) is not maintaining a persistent FCM connection inside the container. Attempted to verify via `waydroid shell` + `ps` but Android's stripped busybox `ps` does not support standard flags — investigation inconclusive.

### No notification bridge package available

```bash
apk search waydroid
# Returns: waydroid, waydroid-nftables, waydroid-openrc, waydroid-pyc,
#          waydroid-sensors, waydroid-sensors-systemd, waydroid-systemd
# No notification bridge package exists in postmarketOS repos
```

`pip show waydroid-notif` returns nothing. No community notification bridge tool available via standard package managers.

### One fluke notification observed

A single WhatsApp notification appeared in GNOME briefly during testing — disappeared before it could be interacted with. Likely occurred because Waydroid was actively foregrounded at that exact moment. Not reproducible.

---

## Fix

No fix currently known. This is a platform-wide unsolved problem across all mobile Linux distributions using Waydroid.

Potential approaches (uninvestigated):

1. **Keep container always running** — prevents freezing, may improve FCM reliability at battery cost
2. **Periodic wake service** — unfreeze container every few minutes to sync notifications, then refreeze
3. **FCM proxy** — route FCM pushes through the host OS notification system (complex, requires significant development work)
4. **waydroid-notif community tool** — third party scripts exist but are not packaged for postmarketOS

## Persistence

N/A — no fix implemented yet.

---

## Upstream

- Waydroid notification bridging is a known open issue in the Waydroid project
- Related: https://github.com/waydroid/waydroid/issues (search "notifications")
- No postmarketOS-specific upstream issue filed yet

## Notes

- Read receipt inconsistency is caused by the same root issue — WhatsApp only syncs when foregrounded
- This is a major consumer usability blocker — users expect WhatsApp notifications to work reliably
- Candidate for NLnet funded milestone: "Reliable Android app notification bridging from Waydroid to host OS"
- One-time fluke notification observed suggests the bridge mechanism exists in some form but is not reliable
