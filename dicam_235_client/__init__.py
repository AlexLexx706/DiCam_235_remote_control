"""Implamentation of control cleint for action camera DiCam 235"""
import socket
import time
import struct
import logging
import re

LOG = logging.getLogger(__name__)

CAMERA_IP = "192.168.25.1"
CAMERA_CONTROL_PORT = 8081


class DiCam235Client:
    """TCP Control client for action camera DiCam 235"""
    RECONNECT_DELAY = 2

    HEADER = b"GPSOCKET"
    RESULT_PATERN = re.compile(b"GPSOCKET(.{6})")
    READ_SIZE = 1024

    CMD_TAKE_PHOTO = 0x0002
    CMD_GET_SETTINGS = 0x0200
    CMD_CHANGE_MODE = 0x0000

    MODE_PHOTO = 0x01
    MODE_VIDEO = 0x00

    ERROR_CODE_OK = 0x02
    ERROR_CODE_FAIL = 0x03

    def __init__(self, ip=CAMERA_IP, port=CAMERA_CONTROL_PORT):
        self.ip = ip
        self.port = port
        self.__sock = None

    def connect(self):
        """Establish connection to the server."""
        while 1:
            try:
                LOG.debug("Connecting to %s:%s..", self.ip, self.port)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.ip, self.port))
                self.__sock = sock
                LOG.debug("Connected.")
                return
            except (socket.timeout, ConnectionRefusedError, OSError) as e:
                LOG.warning("Connection failed:%s", e)
                time.sleep(self.RECONNECT_DELAY)

    def close(self):
        """Stop the client."""
        if self.__sock:
            self.__sock.close()
            self.__sock = None

    def is_connected(self):
        """Check if the client is connected to the server."""
        return self.__sock is not None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def send_cmd(self, cmd: int, param: int | None) -> tuple[int, bytes | int]:
        """Send command to the server and receive response.
        Args:
            cmd (int): Command to send.
            param (int | None): Parameter for the command.
        Returns:
            tuple: Tuple containing the response code and payload
                or error_code.
        Raises:
            ConnectionError - in all case of connection errors
        """
        if not self.__sock:
            raise ConnectionError("Not connected to the server.")

        packet = self.HEADER + struct.pack("<HH", 0x01, cmd)

        if param is not None:
            packet += struct.pack("<B", param)

        LOG.debug("Send packet:%s", packet)
        try:
            self.__sock.sendall(packet)

        except (
            BrokenPipeError, ConnectionResetError,
            socket.timeout, OSError
        ) as e:
            LOG.exception(e)
            self.__sock.close()
            self.__sock = None
            raise ConnectionError("Connection error") from e

        # receive result
        payload = b""
        data = b""
        decode_state = 0

        while 1:
            # read data from socket
            try:
                packet = self.__sock.recv(self.READ_SIZE)
                if not packet:
                    raise ConnectionError("Server closed the connection.")
            # connection error, close socket
            except (socket.timeout, ConnectionResetError, OSError) as e:
                LOG.exception(e)
                self.__sock.close()
                self.__sock = None
                raise ConnectionError("Connection error") from e

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
                    if result_type == self.ERROR_CODE_OK:
                        # return payload
                        if size_or_code == 0:
                            LOG.debug(
                                "result:%s, paylod:%s", result_type, payload)
                            return result_type, payload

                        # collecting payload
                        payload_end = header.end() + size_or_code

                        if len(data) >= payload_end:
                            part = data[header.end(): payload_end]
                            # LOG.debug(f"part:{part}")
                            payload += part
                            data = data[payload_end:]
                            decode_state = 0
                        # waiting for more data
                        else:
                            break
                    # bad response
                    else:
                        LOG.debug(
                            "result:%s, error_code:%s", result_type,
                            size_or_code)
                        return result_type, size_or_code
