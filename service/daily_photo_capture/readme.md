# Daily Photo Capture Service for DiCam 235

This service automatically captures daily photos using the DiCam 235 camera.

## Installation

Copy the service file to systemd:

```bash
sudo cp ./daily_photo_capture.service /etc/systemd/system/
```

Reload systemd configuration:

```bash
sudo systemctl daemon-reload
```

Enable the service to start at boot:

```bash
sudo systemctl enable daily_photo_capture.service
```

Start the service:

```bash
sudo systemctl start daily_photo_capture.service
```

## Service Management

Check service status:

```bash
sudo systemctl status daily_photo_capture.service
```

View service logs:

```bash
journalctl -u daily_photo_capture.service -e
```

Stop the service:

```bash
sudo systemctl stop daily_photo_capture.service
```

Restart the service:

```bash
sudo systemctl restart daily_photo_capture.service
```
