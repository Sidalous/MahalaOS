# Issue 002 — Boot LUKS unlock screen shows full QWERTY keyboard instead of numeric keypad

**Date:** 2026-03-01
**Device:** OnePlus 6T (fajita), postmarketOS edge, GNOME Mobile, systemd
**Severity:** Major
**Status:** Upstream — feature request filed

---

## Summary

When entering the LUKS disk encryption passphrase at boot, users are presented with a full QWERTY keyboard. After boot, the GNOME lock screen correctly shows a numeric PIN pad. The inconsistency is confusing for non-technical users.

---

## Steps to Reproduce

1. Boot a postmarketOS device with LUKS encryption enabled
2. Observe the on-screen keyboard presented for passphrase entry
3. Compare with the lock screen keyboard shown after boot

## Expected

A numeric keypad — consistent with the post-boot lock screen and consistent with the PIN entry paradigm users set during installation.

## Actual

Full QWERTY keyboard. Users must locate and tap individual number keys to enter their PIN.

---

## Investigation

Initial assumption was that `osk-sdl` handled the boot unlock screen. This was incorrect — `osk-sdl` is not installed on this image.

`apk info osk-sdl` revealed the package is actually `unl0kr` (part of `buffybox`). However, `unl0kr` is also not present in the running filesystem or the initramfs.

After extracting and inspecting the initramfs (`/boot/initramfs`, zstandard compressed):

```bash
sudo zstd -d /boot/initramfs -o /tmp/initramfs.cpio
mkdir /tmp/initrd
cd /tmp/initrd && sudo cpio -id < /tmp/initramfs.cpio
```

The binary handling the on-screen keyboard is `buffyboard` (`/usr/bin/buffyboard`), part of the `buffybox` package. It is spawned in `init_functions.sh`:

```sh
if command -v buffyboard 2>/dev/null && \
   echo "handset tablet convertible" | grep "${deviceinfo_chassis:-handset}" >/dev/null; then
        modprobe uinput
        setfont "/usr/share/consolefonts/ter-128n.psf.gz" -C "/dev/$active_console"
        buffyboard &
fi
```

`strings` analysis of the buffyboard binary confirms it reads config from `/etc/buffyboard.conf` and `/etc/buffyboard.conf.d/` — but has no numeric or PIN keyboard mode. Only full QWERTY is available.

---

## Fix

No fix currently available. buffyboard does not support a numeric keyboard mode.

## Persistence

N/A until upstream fix lands.

---

## Upstream

- Feature request filed: https://gitlab.postmarketos.org/postmarketOS/buffybox/-/issues
- The fix requires two changes:
  1. Add a numeric/PIN keyboard mode to buffyboard
  2. Update `init_functions.sh` in `postmarketos-initramfs` to spawn buffyboard in numeric mode for LUKS passphrase entry

## Notes

This is a consumer UX blocker. The inconsistency between the boot unlock screen (full QWERTY) and the post-boot lock screen (numpad) creates confusion and erodes trust on first boot — which is the most critical moment for a new user's impression of the OS.

A workaround is to set a LUKS passphrase that is easy to type on a QWERTY keyboard, but this is not appropriate for a consumer-facing product.
