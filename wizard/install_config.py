"""
install_config.py — reads MahalaOS install configuration.

The config file at /etc/mahalaos/install.conf is written at flash time
by the installer tool. Home installs either have no file or install_type=home.
Franchise and OEM installs set install_type and partner_token here.

Format (simple key=value, no sections):
  install_type=franchise
  partner_token=abc123def456
  os_version=1.0.0
"""

import os

CONFIG_PATH   = "/etc/mahalaos/install.conf"
DEVICE_ID_PATH = "/var/lib/mahalaos/device-id"

DEFAULTS = {
    "install_type":  "home",
    "partner_token": None,
    "os_version":    "unknown",
}


def read_install_config():
    """
    Read install config from CONFIG_PATH.
    Returns a dict with all known keys, falling back to defaults.
    """
    config = dict(DEFAULTS)

    if not os.path.exists(CONFIG_PATH):
        return config

    try:
        with open(CONFIG_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip().lower()
                value = value.strip()
                if key in config or key == "partner_token":
                    config[key] = value if value else None
    except Exception:
        pass

    # Validate install_type
    if config.get("install_type") not in ("home", "franchise", "oem"):
        config["install_type"] = "home"

    return config


def save_device_id(device_id: str):
    """Persist the generated device UUID to disk."""
    try:
        os.makedirs(os.path.dirname(DEVICE_ID_PATH), exist_ok=True)
        with open(DEVICE_ID_PATH, "w") as f:
            f.write(device_id.strip() + "\n")
    except Exception:
        pass


def load_device_id():
    """Load existing device UUID if present, else return None."""
    try:
        with open(DEVICE_ID_PATH) as f:
            val = f.read().strip()
            if val:
                return val
    except Exception:
        pass
    return None
