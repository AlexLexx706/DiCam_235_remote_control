"""This script is used to control the camera manually."""
import time
import logging
import dicam_235_client

LOG = logging.getLogger(__name__)


def main():
    """main loop"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    client = dicam_235_client.DiCam235Client()
    client.connect()
    start_time = time.time()

    while 1:
        try:
            cmd = input()
            LOG.debug("command:%s", cmd.encode())

            # send command
            if not cmd:
                client.send_cmd(client.CMD_TAKE_PHOTO, None)
            elif cmd == "s":
                code, payload = client.send_cmd(client.CMD_GET_SETTINGS, None)
                if code == client.ERROR_CODE_OK:
                    end_tag = b"</Menu>"
                    settings = payload[: payload.find(end_tag) + len(end_tag)]
                    LOG.debug(settings.decode())
                else:
                    LOG.debug("Failed to get settings")
            elif cmd == "p":
                client.send_cmd(client.CMD_CHANGE_MODE, client.MODE_PHOTO)
            elif cmd == "v":
                client.send_cmd(client.CMD_CHANGE_MODE, client.MODE_VIDEO)
        except KeyboardInterrupt:
            LOG.info("Shutting down...")
            client.stop()
            break
        except ConnectionError as e:
            LOG.exception(e)
            LOG.info(
                "Attempting to reconnect, connection duration:%s sec",
                time.time() - start_time)
            start_time = time.time()

            if not client.is_connected():
                client.connect()
            else:
                raise RuntimeError("wrong logic!!!") from e


if __name__ == "__main__":
    main()
