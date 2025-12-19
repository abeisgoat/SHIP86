#!/bin/bash
set -e

INSTALL_DIR="/opt/automon"
SERVICE_NAME="automon"

# Check for root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo ./install.sh)"
    exit 1
fi

# Get the user who ran sudo
RUN_USER="${SUDO_USER:-$USER}"
if [ "$RUN_USER" = "root" ]; then
    echo "Error: Please run with sudo from a non-root user"
    exit 1
fi

echo "Installing automon SD card monitor..."
echo "Exec commands will run as user: $RUN_USER"

# Create install directory
mkdir -p "$INSTALL_DIR"

# Copy files
cp sd_monitor.py "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"

# Create virtual environment and install dependencies
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# Create systemd service
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Automon SD Card Monitor
After=multi-user.target

[Service]
Type=simple
ExecStart=${INSTALL_DIR}/venv/bin/python ${INSTALL_DIR}/sd_monitor.py --user ${RUN_USER}
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

echo "Installation complete!"
echo ""
echo "Commands:"
echo "  sudo systemctl status $SERVICE_NAME   - Check status"
echo "  sudo systemctl stop $SERVICE_NAME     - Stop service"
echo "  sudo systemctl start $SERVICE_NAME    - Start service"
echo "  sudo journalctl -u $SERVICE_NAME -f   - View logs"
