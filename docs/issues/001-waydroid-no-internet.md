# Issue 001 — Waydroid container has no internet connectivity on postmarketOS with nftables

**Date:** 2026-02-28
**Device:** OnePlus 6T (fajita), postmarketOS edge, GNOME Mobile, systemd
**Severity:** Blocker
**Status:** Fixed

---

## Summary

Waydroid runs but shows `IP: UNKNOWN` — Android apps cannot access the internet out of the box on postmarketOS with nftables firewall.

---

## Steps to Reproduce

1. Install postmarketOS edge with systemd on a device
2. Install and start Waydroid
3. Run `waydroid status`
4. Observe `IP: UNKNOWN`
5. Open any Android app requiring internet — it will fail

## Expected

Waydroid container receives an IP, gateway, and DNS automatically from the host's dnsmasq. Android apps can access the internet.

## Actual

Container never gets a DHCP lease. `waydroid status` shows `IP: UNKNOWN`. Manual IP assignment allows ping to raw IPs but apps still fail due to Android's policy routing and missing DNS.

---

## Investigation

The `waydroid0` bridge interface exists and dnsmasq is running on the host at `192.168.240.1`. However DHCP traffic is being silently dropped.

postmarketOS uses nftables as its firewall. The `inet filter` table has `policy drop` on both `input` and `forward` chains. Waydroid creates its own `inet lxc` table with accept rules for `waydroid0`, but the `inet filter` table takes precedence and blocks DHCP before it reaches the lxc rules.

Android also uses policy routing (`ip rule`) with a catch-all `unreachable` rule at priority 32000. Even with a manually assigned IP, routes must be in Android's named routing tables (`eth0`, `local_network`) — not the main table — for traffic to flow.

Without a DHCP lease, Android's `EthernetNetworkFactory` never configures the default route or DNS, leaving `DnsAddresses: [ ]`.

**Time spent debugging:** ~2 hours.

---

## Fix

Two nftables rules on the host, allowing the `waydroid0` bridge interface through the postmarketOS firewall:

```bash
sudo nft add rule inet filter input iifname "waydroid0" accept
sudo nft add rule inet filter forward iifname "waydroid0" accept
```

After applying, restart Waydroid. The container will receive a DHCP lease automatically with IP, default route, and DNS all configured by Android's `EthernetNetworkFactory`.

## Persistence

Systemd service at `/etc/systemd/system/mahala-waydroid-net.service`:

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

[Install]
WantedBy=multi-user.target
```

**Important:** On postmarketOS, `nft` is at `/usr/sbin/nft` — not `/usr/bin/nft`.

Enable with: `sudo systemctl enable --now mahala-waydroid-net.service`

---

## Upstream

- Affects all postmarketOS users running Waydroid with systemd/nftables
- No upstream fix at time of writing
- Fix candidate for postmarketOS wiki and/or postmarketOS-base package

## Notes

This affects any postmarketOS device with systemd and nftables — not just fajita. The fix is simple but requires knowing where to look. A consumer user would have no way to diagnose or fix this.
