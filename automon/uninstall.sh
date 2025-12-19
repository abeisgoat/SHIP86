#!/bin/bash
set -e

INSTALL_DIR="/opt/automon"
SERVICE_NAME="automon"

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./uninstall.sh)"
    exit 1
fi

echo "Uninstalling automon..."

# Stop and disable service
systemctl stop "$SERVICE_NAME" 2>/dev/null || true
systemctl disable "$SERVICE_NAME" 2>/dev/null || true

# Remove service file
rm -f /etc/systemd/system/${SERVICE_NAME}.service
systemctl daemon-reload

# Remove install directory
rm -rf "$INSTALL_DIR"

echo "Uninstall complete!"
