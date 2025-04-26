sudo cp ./daily_photo_capture.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable daily_photo_capture.service
sudo systemctl start daily_photo_capture.service
sudo systemctl status daily_photo_capture.service
journalctl -u daily_photo_capture.service -e

sudo systemctl stop daily_photo_capture.service
sudo systemctl restart daily_photo_capture.service
