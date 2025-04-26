# DiCam 235 Remote Control

A lightweight Python client for **remote control** of the **DiCam 235** action camera over Wi-Fi. This project allows you to connect to the camera's internal Wi-Fi network and send control commands such as shutter release, mode switching, and configuration queries — based on reverse-engineering of the proprietary protocol.

## Features

- 📶 **Wi-Fi connectivity:** Connects to DiCam 235's built-in Wi-Fi access point (default IP `192.168.25.1`).
- 📷 **Photo & Video control:** Send shutter command to take photos or start/stop video recording.
- 🔄 **Switch modes:** Switch between **Photo** and **Video** modes remotely.
- ⚙️ **Camera settings retrieval:** Fetch current camera configuration (returns raw XML data).
- 🕒 **Automated photo capture:** Script for time-based photo sessions (e.g., one photo every hour between 7:00 and 19:00).
- 📺 **Live video stream:** View live video stream via browser or media player at `http://192.168.25.1:8080/?action=stream`.

## Requirements

- **Python 3.10+**
- **Operating system:** Windows, Linux, or macOS
- **Hardware:** DiCam 235 camera with Wi-Fi capability
- **Dependencies:** Only standard Python libraries (`socket`, `logging`, `struct`, `re`, `argparse`, etc.)

> Optional: Tools like `airmon-ng`, `airodump-ng`, and `wireshark` were used for protocol sniffing but are **not** needed to run the client.

## Installation

1. **Connect to the camera Wi-Fi:**
   Turn on Wi-Fi on the DiCam 235 camera and connect your computer to it (SSID and password are shown on the camera screen).

2. **Clone the repository:**
   ```bash
   git clone https://github.com/AlexLexx706/DiCam_235_remote_control.git
   cd DiCam_235_remote_control

3. (Optional) Install as a Python package:
   `pip install .`
    This enables the command-line shortcut dicam_235_keyboard.

4. Run manual control tool:
    `python3 tools/manual_control.py`
    Or, if installed:
    `dicam_235_keyboard`
5. Run automated daily photo capture:
    `python3 tools/daily_photo_capture.py`

## Usage Examples:
1. Manual Camera Control
    Once you run manual_control.py, the script connects to the camera and accepts keyboard input:

    * Press Enter — trigger shutter (photo or video toggle depending on mode)
    * Type p + Enter — switch to Photo mode
    * Type v + Enter — switch to Video mode
    * Type s + Enter — fetch camera settings (XML will be shown in debug logs)
    * Press Ctrl+C — clean exit
    Add --debug to enable detailed logging:
    `dicam_235_keyboard --debug`

2. Scheduled Photo Capture:
The script daily_photo_capture.py allows automated time-based photo shooting (e.g., every hour from 7:00 to 19:00).

### Example:
`python3 tools/daily_photo_capture.py --start-hour 9 --end-hour 17 --photos-per-interval 8`

### Options:
    --start-hour (default: 7)
    --end-hour (default: 19)
    --photos-per-interval (default: 12)
    --debug – verbose logging

Interrupt with Ctrl+C to stop cleanly.

3. View Live Stream:
While connected to the camera’s Wi-Fi, open your browser or VLC and go to:
`http://192.168.25.1:8080/?action=stream`

This stream runs independently of the control client.
## Contact:
Author: Alexey Kalmykov

📧 Email: alexlexx1@gmail.com

🌐 Website: alexlexx.com

🐙 GitHub: @AlexLexx706

## License:
This project is licensed under the MIT License.
See the LICENSE.txt file for details.
