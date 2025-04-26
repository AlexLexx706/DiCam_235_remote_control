# Wi-Fi Connection Help

This document explains how to manage Wi-Fi connections using `nmcli` commands.

## Enable Wi-Fi

```bash
sudo nmcli radio wifi on
```

## List Available Wi-Fi Networks

```bash
sudo nmcli dev wifi list
```

## Show Connection Priorities

```bash
sudo nmcli -f autoconnect-priority,name c
```

## Connect to a Wi-Fi Network

Example commands to connect:

```bash
sudo nmcli dev wifi connect TIM-34779126 password YOUR_PASSWORD
sudo nmcli dev wifi connect DcCan235 password YOUR_PASSWORD
```

## Set Connection Priority

Higher priority values mean the system will prefer those connections:

```bash
sudo nmcli connection modify DcCan235 connection.autoconnect-priority 10
sudo nmcli connection modify TIM-34779126 connection.autoconnect-priority 9
```

## Delete a Saved Connection

To remove a network from saved connections:

```bash
sudo nmcli connection delete DcCan235
sudo nmcli connection delete TIM-34779126
```

## Manually Bring Up a Connection

To manually activate a connection:

```bash
sudo nmcli connection up DcCan235
sudo nmcli connection up TIM-34779126
```

---

**Note:**  
Replace `YOUR_PASSWORD` with the actual password for each Wi-Fi network.