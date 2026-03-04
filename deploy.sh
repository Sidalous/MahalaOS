#!/bin/bash
# deploy.sh — transfer and install the MahalaOS wizard to the OnePlus 6T over USB SSH
#
# Usage:
#   ./deploy.sh [user@host]
#
# Default host: user@172.16.42.1 (postmarketOS USB networking default)
# Override: ./deploy.sh user@192.168.1.x

set -e

HOST="${1:-user@172.16.42.1}"
REMOTE_TMP="/tmp/mahalaos-wizard"
REMOTE_INSTALL="/usr/lib/mahalaos/wizard"

echo "→ Deploying MahalaOS Wizard to $HOST"

# 1. Copy wizard files (no TTY needed for scp)
echo "→ Copying files..."
ssh "$HOST" "mkdir -p $REMOTE_TMP"
scp -r wizard/ "$HOST:$REMOTE_TMP/"

# 2. Install — use -t to allocate a TTY so sudo/doas can prompt for password
echo "→ Installing (you may be prompted for your device password)..."
ssh -t "$HOST" "
  sudo mkdir -p $REMOTE_INSTALL &&
  sudo cp -r $REMOTE_TMP/wizard/* $REMOTE_INSTALL/ &&
  sudo chmod +x $REMOTE_INSTALL/mahalaos-wizard.py &&
  sudo cp $REMOTE_INSTALL/polkit/org.mahalaos.wizard.policy \
    /usr/share/polkit-1/actions/org.mahalaos.wizard.policy &&
  sudo mkdir -p /var/lib/mahalaos &&
  mkdir -p ~/.config/autostart &&
  cp $REMOTE_INSTALL/data/mahalaos-wizard.desktop ~/.config/autostart/
"

echo ""
echo "✓ Deploy complete."
echo ""
echo "To launch on the device screen, run this ON THE DEVICE (not over SSH):"
echo "  python3 $REMOTE_INSTALL/mahalaos-wizard.py --dev"
echo ""
echo "Or if your device has a terminal app, open it and run the command above."
echo ""
echo "To reset the wizard (run it again from the start):"
echo "  sudo rm -f /var/lib/mahalaos/wizard-complete"
