"""script for remore control of DiCam 235"""

import socket
import threading
import time
import struct
import logging
import re

LOG = logging.getLogger(__name__)

CAMERA_IP = "192.168.25.1"
CONTROL_PORT = 8081

# responce packet structure: header 8 bytes(GPSOCKET) + packet type 2 bytes + packet id 2 bytes + [payload size 2 bytes, payload]
# control packets
# GET_STATUS_PACKET =                     bytes.fromhex("47 50 53 4f 43 4b 45 54  01 00 00 01")

# REQUEST_SETTINGS_PACKET =               bytes.fromhex("47 50 53 4f 43 4b 45 54  01 00 00 02")
# GOOD_RESP_REQUEST_SETTINGS_PACKET=      bytes.fromhex("47 50 53 4f 43 4b 45 54  02 00 00 02 f2 00")


# MAKE_PHOTO_PACKET =                     bytes.fromhex("47 50 53 4f 43 4b 45 54  01 00 02 00")
# GOOD_RESP_MAKE_PHOTO_PACKET =           bytes.fromhex("47 50 53 4f 43 4b 45 54  02 00 02 00 00 00")
# BAD_RESP_MAKE_PHOTO_PACKET =            bytes.fromhex("47 50 53 4f 43 4b 45 54  03 00 02 00 fd ff")

# SET_PHOTO_MODE_PACKET =                 bytes.fromhex("47 50 53 4f 43 4b 45 54  01 00 00 00 01")
# GOOD_RESP_SET_PHOTO_MODE_PACKET =       bytes.fromhex("47 50 53 4f 43 4b 45 54  02 00 00 00 00 00")

# SET_VIDEO_MODE_PACKET =                 bytes.fromhex("47 50 53 4f 43 4b 45 54  01 00 00 00 00")
# GOOD_RESP_SET_VIDEO_MODE_PACKET =       bytes.fromhex("47 50 53 4f 43 4b 45 54  02 00 00 00 00 00")

# RECONNECT_DELAY = 2                      # Delay before attempting to reconnect


class TCPClient:
    HEADER = b"GPSOCKET"
    RESULT_PATERN = re.compile(b"GPSOCKET(.{6})")
    READ_SIZE = 1024

    TAKE_PHOTO_CMD = 0x0002
    GET_SETTINGS_CMD = 0x0200
    CHANGE_MODE_CMD = 0x0000

    MODE_PHOTO = 0x01
    MODE_VIDEO = 0x00

    class ProtocolError(RuntimeError):
        """Custom exception for protocol errors."""

        pass

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = None
        self.connected = False
        self.__decode_state = 0
        self.lock = threading.Lock()
        self.stop_event = threading.Event()

    def connect(self):
        """Establish connection to the server."""
        while not self.stop_event.is_set():
            try:
                LOG.debug(f"Connecting to {self.server_ip}:{self.server_port}...")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.server_ip, self.server_port))
                with self.lock:
                    self.sock = sock
                    self.connected = True
                LOG.debug("Connected.")
                return
            except Exception as e:
                LOG.warning(f"Connection failed:{e}")
                time.sleep(RECONNECT_DELAY)

    def __send_packet(self, cmd, param):
        """Send packet to the camera and receive response.
        Args:
            cmd (int): Command ID.
            param (int): Parameter for the command.
        Returns:
            bytes: Response payload.
        Raises:
            ProtocolError: If the response indicates an error.
        """
        packet = self.HEADER + struct.pack("<HH", 0x01, cmd)

        if param is not None:
            packet += struct.pack("<B", param)

        LOG.debug(f"Send packet: {packet}")
        self.sock.sendall(packet)

        # receive result
        payload = b""
        data = b""
        decode_state = 0

        while not self.stop_event.is_set():
            packet = self.sock.recv(self.READ_SIZE)
            if not packet:
                raise ConnectionError("Server closed the connection.")
            data += packet
            # analyze received data
            while 1:
                # search header
                if decode_state == 0:
                    header = self.RESULT_PATERN.search(data)

                    # packet header found
                    if header is not None:
                        result_type, _cmd_id, size_or_code = struct.unpack(
                            "<HHH", header.group(1)
                        )
                        decode_state = 1
                    else:
                        # packet header not found, waiting for more data
                        break

                # reading payload
                if decode_state == 1:
                    # good response, reading payload
                    if result_type == 0x02:
                        # return payload
                        if size_or_code == 0:
                            return payload

                        # collecting payload
                        payload_end = header.end() + size_or_code

                        if len(data) >= payload_end:
                            part = data[header.end() : payload_end]
                            # LOG.debug(f"part:{part}")
                            payload += part
                            data = data[payload_end:]
                            decode_state = 0
                        # waiting for more data
                        else:
                            break
                    # bad response
                    else:
                        raise self.ProtocolError(
                            f"Error in response", result_type, size_or_code
                        )

    def loop(self):
        """main loop"""
        start_time = time.time()

        while not self.stop_event.is_set():
            if not self.connected:
                LOG.debug(f"Connetion period:{time.time() - start_time}")
                self.connect()
                start_time = time.time()
            try:
                cmd = input()
                LOG.debug(f"command:{cmd.encode()}")

                # send command
                if not cmd:
                    self.__send_packet(self.TAKE_PHOTO_CMD, None)
                elif cmd == "s":
                    settings = self.__send_packet(self.GET_SETTINGS_CMD, None)
                    end_tag = b"</Menu>"
                    settings = settings[: settings.find(end_tag) + len(end_tag)]
                    LOG.debug(settings.decode())
                elif cmd == "p":
                    self.__send_packet(self.CHANGE_MODE_CMD, self.MODE_PHOTO)
                elif cmd == "v":
                    self.__send_packet(self.CHANGE_MODE_CMD, self.MODE_VIDEO)
            except self.ProtocolError as e:
                LOG.warning(e)
            except Exception as e:
                print("Receive error:", e)
                self.connected = False
                with self.lock:
                    if self.sock:
                        self.sock.close()
                        self.sock = None
                print("Attempting to reconnect...")

    def run(self):
        self.connect()
        self.loop()

    def stop(self):
        self.stop_event.set()
        with self.lock:
            if self.sock:
                self.sock.close()


def main():
    logging.basicConfig(level=logging.DEBUG)
    client = TCPClient(CAMERA_IP, CONTROL_PORT)
    try:
        client.run()
    except KeyboardInterrupt:
        LOG.info("Shutting down...")
        client.stop()


if __name__ == "__main__":
    main()
