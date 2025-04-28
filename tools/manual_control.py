"""This script is used to control the camera manually."""
import time
import logging
import re
import os
import dicam_235_client

LOG = logging.getLogger(__name__)

IMAGES_DIR = "images"


def main():
    """main loop"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    try:
        os.mkdir(IMAGES_DIR)
    except FileExistsError as e:
        LOG.debug(e)

    client = dicam_235_client.DiCam235Client()
    client.connect()
    start_time = time.time()

    while 1:
        try:
            cmd = input()
            LOG.debug("command:%s", cmd.encode())

            # 1. take photo
            if not cmd:
                client.send_cmd(client.CMD_TAKE_PHOTO, None)
            # 2. get settings
            elif cmd == "settings":
                code, payload = client.send_cmd(
                    client.CMD_GET_SETTINGS, None, multy_packet=True)
                if code == client.ERROR_CODE_OK:
                    end_tag = b"</Menu>"
                    settings = payload[: payload.find(end_tag) + len(end_tag)]
                    LOG.debug(settings.decode())
                else:
                    LOG.debug("Failed to get settings")
            # 3. set photo mode
            elif cmd == "photo_mode":
                client.send_cmd(client.CMD_CHANGE_MODE, client.MODE_PHOTO)
            # 4. set video mode
            elif cmd == "video_mode":
                client.send_cmd(client.CMD_CHANGE_MODE, client.MODE_VIDEO)
            # 5. get files count
            elif cmd == "files_count":
                # request files count
                error_code, payload = client.send_cmd(
                    client.CMD_REQUEST_FILES_COUNT, None)

                if error_code == client.ERROR_CODE_OK:
                    count = int.from_bytes(payload, byteorder='little')
                    print(f"Number of files in the camera: {count}")
            # 8. upload all files
            elif cmd == "upload_all":
                error_code, payload = client.send_cmd(
                    client.CMD_REQUEST_FILES_COUNT, None)

                if error_code == client.ERROR_CODE_OK:
                    count = int.from_bytes(payload, byteorder='little')
                    for file_num in range(count):
                        # request files count
                        error_code, payload = client.send_cmd(
                            client.CMD_REQUEST_FILE,
                            file_num.to_bytes(2, byteorder='little'),
                            multy_packet=True)

                        if error_code == client.ERROR_CODE_OK:
                            file_path = os.path.join(
                                IMAGES_DIR, f'{file_num}.jpg')
                            with open(file_path, 'wb') as file:
                                file.write(payload)
                            LOG.info(
                                "file created:%s size:%s", file_path,
                                len(payload))
            else:
                # 6. get file by number\
                res = re.match(r"file\s+(\d+)", cmd)
                if res is not None:
                    file_num = int(res.group(1))
                    # request files count
                    error_code, payload = client.send_cmd(
                        client.CMD_REQUEST_FILE,
                        file_num.to_bytes(2, byteorder='little'),
                        multy_packet=True)

                    if error_code == client.ERROR_CODE_OK:
                        file_path = os.path.join(IMAGES_DIR, f'{file_num}.jpg')
                        with open(file_path, 'wb') as file:
                            file.write(payload)
                        LOG.info(
                            "file created:%s size:%s", file_path,
                            len(payload))

                # 7. get preview by number
                res = re.match(r"preview\s+(\d+)", cmd)
                if res is not None:
                    file_num = int(res.group(1))
                    # request files count
                    error_code, payload = client.send_cmd(
                        client.CMD_REQUEST_PREVIEW,
                        file_num.to_bytes(2, byteorder='little'),
                        multy_packet=True)
                    if error_code == client.ERROR_CODE_OK:
                        file_path = os.path.join(
                            IMAGES_DIR, f'preview_{file_num}.jpg')

                        with open(file_path, 'wb') as file:
                            file.write(payload)

                        LOG.info(
                            "preview file created:%s size:%s", file_path,
                            len(payload))

        except KeyboardInterrupt:
            LOG.info("Shutting down...")
            client.close()
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
