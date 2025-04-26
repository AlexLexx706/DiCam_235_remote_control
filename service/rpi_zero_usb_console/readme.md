sudo systemctl enable serial-getty@ttyGS0.service
sudo systemctl start serial-getty@ttyGS0.service
sudo systemctl status serial-getty@ttyGS0.service

sudo systemctl edit serial-getty@ttyGS0.service

[Unit]
Description=Serial Getty on ttyGS0 (early start)
ConditionPathExists=/dev/ttyGS0
After=dev-ttyGS0.device
After=systemd-user-sessions.service


sudo systemctl daemon-reload
journalctl -u serial-getty@ttyGS0.service -e

# how to add terminal at usb-otg of RPI-zero:
1. need to add ad the end of file /boot/firmware/config.txt this line dtoverlay=dwc2
example of /boot/firmware/config.txt:
`# For more options and information see
# http://rptl.io/configtxt
# Some settings may impact device functionality. See link above for details

# Uncomment some or all of these to enable the optional hardware interfaces
#dtparam=i2c_arm=on
#dtparam=i2s=on
#dtparam=spi=on

# Enable audio (loads snd_bcm2835)
dtparam=audio=on

# Additional overlays and parameters are documented
# /boot/firmware/overlays/README

# Automatically load overlays for detected cameras
camera_auto_detect=1

# Automatically load overlays for detected DSI displays
display_auto_detect=1

# Automatically load initramfs files, if found
auto_initramfs=1

# Enable DRM VC4 V3D driver
dtoverlay=vc4-kms-v3d
max_framebuffers=2

# Don't have the firmware create an initial video= setting in cmdline.txt.
# Use the kernel's default instead.
disable_fw_kms_setup=1

# Run in 64-bit mode
arm_64bit=1

# Disable compensation for displays with overscan
disable_overscan=1

# Run as fast as firmware / board allows
arm_boost=1

[cm4]
# Enable host mode on the 2711 built-in XHCI USB controller.
# This line should be removed if the legacy DWC2 controller is required
# (e.g. for USB device mode) or if USB support is not required.
otg_mode=1

[cm5]
dtoverlay=dwc2,dr_mode=host

[all]
enable_uart=1

dtoverlay=dwc2
`
2. need add loading of usb driver and usb-consoe drives at cmdline.txt: add at the end of line of file /boot/firmware/cmdline.txt this: modules-load=dwc2,g_serial
example of /boot/firmware/cmdline.txt:
`console=serial0,115200 console=tty1 root=PARTUUID=ae82db81-02 rootfstype=ext4 fsck.repair=yes rootwait quiet splash plymouth.ignore-serial-consoles cfg80211.ieee80211_regdom=IT modules-load=dwc2,g_serial`
3. need to create terminal servise:
`sudo systemctl enable serial-getty@ttyGS0.service`
`sudo systemctl edit serial-getty@ttyGS0.service`

[Unit]
Description=Serial Getty on ttyGS0 (early start)
ConditionPathExists=/dev/ttyGS0
After=dev-ttyGS0.device
After=systemd-user-sessions.service

sudo systemctl daemon-reload
journalctl -u serial-getty@ttyGS0.service -e

