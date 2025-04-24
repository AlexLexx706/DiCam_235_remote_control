"""script for remore control of DiCam 235"""
import socket
import threading
import time

CAMERA_IP = "192.168.25.1"
CONTROL_PORT = 8081
VIDEO_STREAM_PORT = 8080

# control packets
GET_STATUS_PACKET =                     bytes.fromhex("47 50 53 4f 43 4b 45 54  01 00 00 01")
REQUEST_SETTINGS_PACKET =               bytes.fromhex("47 50 53 4f 43 4b 45 54  01 00 00 02")
GOOD_RESP_REQUEST_SETTINGS_PACKET=      bytes.fromhex("47 50 53 4f 43 4b 45 54  02 00 00 02 f2 00")

MAKE_PHOTO_PACKET =                     bytes.fromhex("47 50 53 4f 43 4b 45 54  01 00 02 00")
GOOD_RESP_MAKE_PHOTO_PACKET =           bytes.fromhex("47 50 53 4f 43 4b 45 54  02 00 02 00 00 00")
BAD_RESP_MAKE_PHOTO_PACKET =            bytes.fromhex("47 50 53 4f 43 4b 45 54  03 00 02 00 fd ff")

SET_PHOTO_MODE_PACKET =                 bytes.fromhex("47 50 53 4f 43 4b 45 54  01 00 00 00 01")
GOOD_RESP_SET_PHOTO_MODE_PACKET =       bytes.fromhex("47 50 53 4f 43 4b 45 54  02 00 00 00 00 00")

SET_VIDEO_MODE_PACKET =                 bytes.fromhex("47 50 53 4f 43 4b 45 54  01 00 00 00 00")
GOOD_RESP_SET_VIDEO_MODE_PACKET =       bytes.fromhex("47 50 53 4f 43 4b 45 54  02 00 00 00 00 00")

RECONNECT_DELAY = 2                      # Delay before attempting to reconnect

class TCPClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = None
        self.connected = False
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def connect(self):
        while not self.stop_event.is_set():
            try:
                print(f"Connecting to {self.server_ip}:{self.server_port}...")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.server_ip, self.server_port))
                with self.lock:
                    self.sock = sock
                    self.connected = True
                print("Connected.")
                return
            except Exception as e:
                print("Connection failed:", e)
                time.sleep(RECONNECT_DELAY)

    def send(self, data):
        with self.lock:
            if self.sock:
                try:
                    self.sock.sendall(data)
                    print(f"Send data:{data}")
                except Exception as e:
                    print("Send error:", e)
                    self.connected = False

    def receive_loop(self):
        start_time = time.time()
        while not self.stop_event.is_set():
            if not self.connected:
                print(f"Connetion period:{time.time() - start_time}")
                self.connect()
                start_time = time.time()
                self.start_threads()
            try:
                data = self.sock.recv(4096)
                if not data:
                    raise ConnectionError("Server closed the connection.")
                print("Received:", data)
            except Exception as e:
                print("Receive error:", e)
                self.connected = False
                with self.lock:
                    if self.sock:
                        self.sock.close()
                        self.sock = None
                print("Attempting to reconnect...")

    def enter_listener(self):
        while not self.stop_event.is_set():
            try:
                res = input()
                print(f"res:{res.encode()}")
                if self.connected:
                    if not res:
                        self.send(MAKE_PHOTO_PACKET)
                    elif res == 's':
                        self.send(REQUEST_SETTINGS_PACKET)
                    elif res == 'p':
                        self.send(SET_PHOTO_MODE_PACKET)
                    elif res == 'v':
                        self.send(SET_VIDEO_MODE_PACKET)
                    print("Sent packet on Enter.")
            except Exception as e:
                print("Enter listener error:", e)

    def start_threads(self):
        # Start or restart periodic and input threads
        threading.Thread(target=self.enter_listener, daemon=True).start()

    def run(self):
        self.connect()
        self.start_threads()
        self.receive_loop()

    def stop(self):
        self.stop_event.set()
        with self.lock:
            if self.sock:
                self.sock.close()

def main():
    client = TCPClient(CAMERA_IP, CONTROL_PORT)
    try:
        client.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        client.stop()

if __name__ == '__main__':
    main()
