## Set of Commands for Capturing WiFi Traffic and Reverse-Engineering Camera Protocol:
`sudo airmon-ng start wlp0s20f3`
`sudo airmon-ng stop wlp0s20f3mon`

### Remove unneeded processes:
`sudo airmon-ng check kill`

### Verifying available networks:
`sudo airodump-ng wlp0s20f3mon`

### Capture WiFi traffic:
`sudo airodump-ng --bssid 84:EA:97:E0:12:38 --essid DcCan235 -c 7 -w dump wlp0s20f3mon`

### Decode dump:
`airdecap-ng -e DcCan235 -p SupperStrongPassword dump-01.cap`

### Restart WiFi client
`sudo service NetworkManager restart`

### Run Wireshark to Analyze the Recorded Log:
`wireshark`
