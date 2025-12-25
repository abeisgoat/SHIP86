#!/usr/bin/env python3
"""
SD Card Monitor - Detects insertion and removal of SD cards.
Executes signed cart.yaml only if signature is valid.
"""

import argparse
import os
import pwd
import signal
import time
import subprocess
import pyudev
import yaml
import sys

TRUSTED_PUBKEY = "/etc/cart_trust/allowed_signers"
SIGNATURE_NAMESPACE = "cart"


def is_sd_card(device):
    """Check if the device is an SD card (not a partition)."""
    if not device.device_node or device.device_type != "disk":
        return False

    node = device.device_node

    # Native SD card readers (mmcblk*)
    if "mmcblk" in node:
        return True

    # USB card readers - any removable USB storage
    if node.startswith("/dev/sd"):
        if device.properties.get("ID_BUS") == "usb":
            return True
        if device.properties.get("DEVTYPE") == "disk":
            # Check sysfs for removable flag
            try:
                removable_path = f"/sys/block/{node.split('/')[-1]}/removable"
                with open(removable_path) as f:
                    if f.read().strip() == "1":
                        return True
            except (IOError, OSError):
                pass

    return False


def has_media(device):
    """Check if the device has media inserted."""
    # Check for partition table or filesystem
    if device.properties.get("ID_PART_TABLE_TYPE"):
        return True
    if device.properties.get("ID_FS_TYPE"):
        return True
    # Check device size through sysfs
    try:
        name = device.device_node.split("/")[-1]
        with open(f"/sys/block/{name}/size") as f:
            return int(f.read().strip()) > 0
    except (IOError, OSError, ValueError):
        return False


def get_mount_point(device_node, timeout=5):
    """Wait for device to be mounted and return mount point."""
    # Check for partitions (e.g., /dev/sdd1, /dev/mmcblk0p1)
    partitions = []
    dev_name = device_node.split("/")[-1]

    for _ in range(timeout * 2):
        # Find partitions for this device
        try:
            for entry in os.listdir("/sys/block/" + dev_name):
                if entry.startswith(dev_name):
                    partitions.append("/dev/" + entry)
        except OSError:
            pass

        # If no partitions, the device itself might be formatted
        if not partitions:
            partitions = [device_node]

        # Check /proc/mounts for mount points
        try:
            with open("/proc/mounts") as f:
                for line in f:
                    parts = line.split()
                    if parts[0] in partitions:
                        return parts[1]
        except IOError:
            pass

        time.sleep(0.5)

    return None

def verify_cart_signature(cart_path):
    sig_path = cart_path + ".sig"

    if not os.path.exists(sig_path):
        print("ERROR: cart.yaml.sig missing")
        return False

    if not os.path.exists(TRUSTED_PUBKEY):
        print("ERROR: Trusted public key missing")
        return False

    try:
        with open(cart_path, "rb") as f:
            subprocess.check_call([
                "ssh-keygen", "-Y", "verify",
                "-f", TRUSTED_PUBKEY,
                "-I", SIGNATURE_NAMESPACE,
                "-n", SIGNATURE_NAMESPACE,
                "-s", sig_path,
                "-"
            ], stdin=f)

        print("Signature verification OK")
        return True

    except subprocess.CalledProcessError:
        print("ERROR: Signature verification FAILED")
        return False

def get_user_display_env(uid):
    """Get display-related environment variables from user's session."""
    display_vars = {}
    target_vars = ["DISPLAY", "WAYLAND_DISPLAY", "XAUTHORITY", "DBUS_SESSION_BUS_ADDRESS"]

    # Find a process owned by this user and read its environment
    try:
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            try:
                stat_path = f"/proc/{pid}/stat"
                environ_path = f"/proc/{pid}/environ"

                # Check if process belongs to user
                if os.stat(stat_path).st_uid != uid:
                    continue

                # Read environment
                with open(environ_path, "rb") as f:
                    env_data = f.read().decode("utf-8", errors="ignore")
                    for item in env_data.split("\0"):
                        if "=" in item:
                            key, val = item.split("=", 1)
                            if key in target_vars and key not in display_vars:
                                display_vars[key] = val

                # Stop if we found DISPLAY or WAYLAND_DISPLAY
                if "DISPLAY" in display_vars or "WAYLAND_DISPLAY" in display_vars:
                    break
            except (IOError, OSError, PermissionError):
                continue
    except OSError:
        pass

    return display_vars


def start_cart_process(mount_point, run_as_user=None):
    """Check for cart.yaml, parse it, and start the process if found."""
    cart_path = os.path.join(mount_point, "cart.yaml")
    if not os.path.exists(cart_path):
        print("No cart.yaml detected")
        return None

    print(f"Found cart.yaml at {cart_path}")

    if not verify_cart_signature(cart_path):
        print("Execution blocked (untrusted cart)")
        return None
                
    with open(cart_path) as f:
        config = yaml.safe_load(f)

    if not config or "exec" not in config:
        print("No 'exec' field in cart.yaml")
        return None

    script = config["exec"]

    # Set up user switching if specified
    preexec_fn = None
    env = os.environ.copy()
    if run_as_user:
        pw = pwd.getpwnam(run_as_user)
        uid, gid = pw.pw_uid, pw.pw_gid
        env["HOME"] = pw.pw_dir
        env["USER"] = run_as_user
        env["LOGNAME"] = run_as_user
        env["XDG_RUNTIME_DIR"] = f"/run/user/{uid}"

        # Get display environment from user's session
        user_env = get_user_display_env(uid)
        env.update(user_env)

        def switch_user():
            os.setgid(gid)
            os.setuid(uid)

        preexec_fn = switch_user
        print(f"Executing as {run_as_user}: {script}")
    else:
        print(f"Executing: {script}")

    return subprocess.Popen(
        script, shell=True, cwd=mount_point,
        start_new_session=True, preexec_fn=preexec_fn, env=env
    )


def kill_cart_process(proc):
    """Kill a running cart process and all its children."""
    if proc and proc.poll() is None:
        pgid = os.getpgid(proc.pid)
        print(f"Killing process group {pgid}")
        try:
            os.killpg(pgid, signal.SIGTERM)
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(pgid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def monitor(run_as_user=None):
    context = pyudev.Context()
    # Use 'udev' source only to avoid duplicate kernel events
    monitor = pyudev.Monitor.from_netlink(context, source="udev")
    monitor.filter_by(subsystem="block")

    print("Monitoring for SD cards... (Ctrl+C to exit)")
    if run_as_user:
        print(f"Exec commands will run as: {run_as_user}")

    last_event = None
    running_processes = {}  # device_node -> process

    try:
        for device in iter(monitor.poll, None):
            if not is_sd_card(device):
                continue

            if device.action == "add":
                event = ("insert", device.device_node)
            elif device.action == "remove":
                event = ("remove", device.device_node)
            elif device.action == "change":
                event = ("insert" if has_media(device) else "remove", device.device_node)
            else:
                continue

            # Skip duplicate events
            if event == last_event:
                continue
            last_event = event

            device_node = event[1]

            if event[0] == "insert":
                print(f"SD card inserted: {device_node}")
                mount_point = get_mount_point(device_node)
                if mount_point:
                    proc = start_cart_process(mount_point, run_as_user)
                    if proc:
                        running_processes[device_node] = proc
                else:
                    print("Card not mounted")
            else:
                print(f"SD card removed: {device_node}")
                if device_node in running_processes:
                    kill_cart_process(running_processes.pop(device_node))

    except KeyboardInterrupt:
        print("\nStopping...")
        for proc in running_processes.values():
            kill_cart_process(proc)
        print("Stopped.")


if __name__ == "__main__":
    try:
        import pyudev
    except ImportError:
        print("Error: pip install pyudev")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Monitor SD cards and run cart.yaml scripts")
    parser.add_argument("--user", help="Run exec commands as this user")
    args = parser.parse_args()

    monitor(run_as_user=args.user)
