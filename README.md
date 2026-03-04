# MahalaOS Setup Wizard

First-boot setup experience for MahalaOS — a consumer-focused Linux phone OS built on postmarketOS.

## Structure

```
wizard/
├── mahalaos-wizard.py      # Main application entry point
├── screens/
│   ├── base.py             # Base screen class (shared layout/navigation)
│   ├── welcome.py          # Screen 1: Welcome
│   ├── language.py         # Screen 2: Language & Region [stub]
│   ├── wifi.py             # Screen 3: WiFi connection (nmcli)
│   ├── sim.py              # Screen 4: SIM detection [stub - ModemManager]
│   ├── honest.py           # Screen 5: What works / what doesn't
│   ├── whatsapp.py         # Screen 6: WhatsApp/Waydroid setup [stub]
│   └── done.py             # Screen 7: All done
├── data/
│   └── mahalaos-wizard.desktop   # Autostart entry
└── polkit/
    └── org.mahalaos.wizard.policy  # Polkit privileges
```

## Requirements

- Python 3.x
- GTK4 (`python-gobject` / `py3-gobject3` on Alpine/postmarketOS)
- libadwaita (`libadwaita` on Alpine)
- NetworkManager + nmcli (for WiFi screen)
- ModemManager (for SIM screen — stub for now)

Install on postmarketOS:
```sh
sudo apk add py3-gobject3 gtk4 libadwaita networkmanager
```

## Running

### Dev mode (for testing — bypasses completion check, allows window close):
```sh
python3 wizard/mahalaos-wizard.py --dev
```

### Production mode:
```sh
python3 wizard/mahalaos-wizard.py
```

### Reset wizard (to re-run on device):
```sh
sudo rm -f /var/lib/mahalaos/wizard-complete
```

## Deploy to Device

```sh
chmod +x deploy.sh
./deploy.sh user@172.16.42.1    # USB SSH default
```

## Screen Status

| Screen     | Status        | Notes                                      |
|------------|---------------|--------------------------------------------|
| Welcome    | ✅ Complete   |                                            |
| Language   | 🔧 Stub       | Shows placeholder values                   |
| WiFi       | ✅ Complete   | nmcli scan + connect + verify              |
| SIM        | 🔧 Stub       | Needs ModemManager DBus integration        |
| Honest     | ✅ Complete   | Feature status list                        |
| WhatsApp   | 🔧 Stub       | Needs Waydroid state check + launch        |
| Done       | ✅ Complete   | Flag file written, app quick-launch        |

## Completion Flag

The wizard writes `/var/lib/mahalaos/wizard-complete` on finish.
Autostart checks for this file before launching the wizard.
