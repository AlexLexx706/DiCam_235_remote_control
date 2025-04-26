# USB Console on Raspberry Pi Zero

This guide explains how to configure a Raspberry Pi Zero to connect to a terminal via USB-OTG.

## Setup

### 1. Edit `config.txt`

Append the following line to the end of `/boot/firmware/config.txt`:

```bash
dtoverlay=dwc2
```

### 2. Edit `cmdline.txt`

Append the following text to the single line in `/boot/firmware/cmdline.txt`:

```bash
modules-load=dwc2,g_serial
```

**Example `cmdline.txt`:**

```bash
console=serial0,115200 console=tty1 root=PARTUUID=ae82db81-02 rootfstype=ext4 fsck.repair=yes rootwait quiet splash plymouth.ignore-serial-consoles cfg80211.ieee80211_regdom=IT modules-load=dwc2,g_serial
```

---

### 3. Configure systemd Terminal Service

Enable and configure the terminal service on `/dev/ttyGS0`.

Run the following commands:

```bash
sudo systemctl enable serial-getty@ttyGS0.service
sudo systemctl start serial-getty@ttyGS0.service
sudo systemctl status serial-getty@ttyGS0.service
```

To customize the service, edit it:

```bash
sudo systemctl edit serial-getty@ttyGS0.service
```

Insert the following content:

```ini
[Unit]
Description=Serial Getty on ttyGS0 (early start)
ConditionPathExists=/dev/ttyGS0
After=dev-ttyGS0.device
After=systemd-user-sessions.service
```

Apply the changes:

```bash
sudo systemctl daemon-reload
```

Check service logs:

```bash
journalctl -u serial-getty@ttyGS0.service -e
```

---

## Result

After rebooting, the Raspberry Pi Zero will appear as a USB serial console via the OTG port.
