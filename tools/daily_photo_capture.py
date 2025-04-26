"""
This script captures photos from a camera at regular intervals during the day.
"""
import math
import time
import datetime
import logging
import argparse
import dicam_235_client

LOG = logging.getLogger(__name__)

START_HOUR = 7
END_HOUR = 19
PHOTOS_PER_INTERVAL = 12

CMD_INTERVAL_SECONDS = 1.0
MAX_ATTEMPTS = 3


def take_photo():
    """Take a photo using the camera client."""
    client = dicam_235_client.DiCam235Client()
    photos_attemps = 0
    with client:
        while photos_attemps < MAX_ATTEMPTS:
            try:
                # try to take a photo
                code, _ = client.send_cmd(client.CMD_TAKE_PHOTO, None)
                if code == client.ERROR_CODE_OK:
                    return
                else:
                    time.sleep(CMD_INTERVAL_SECONDS)
                    # trying to change mode to video and back to photo
                    code, _ = client.send_cmd(
                        client.CMD_CHANGE_MODE, client.MODE_VIDEO)

                    time.sleep(CMD_INTERVAL_SECONDS)
                    code, _ = client.send_cmd(
                        client.CMD_CHANGE_MODE, client.MODE_PHOTO)

                    time.sleep(CMD_INTERVAL_SECONDS)
                    photos_attemps += 1
            except ConnectionError as e:
                LOG.warning("Connection error: %s, trying to reconnect...", e)
                client.connect()


def is_time_to_shoot(now, start_hour, end_hour):
    """Check if the current time is within the shooting window."""
    print(f"now.hour:{now.hour}")
    return start_hour <= now.hour < end_hour


def main():
    """Main function to run the daily photo capture script."""
    parser = argparse.ArgumentParser(description="Daily photo capture script.")

    parser.add_argument(
        "--start-hour", type=int, default=START_HOUR,
        help=f"Start hour, default:{START_HOUR}")

    parser.add_argument(
        "--end-hour", type=int, default=END_HOUR,
        help=f"End hour, default:{END_HOUR}")

    parser.add_argument(
        "--photos-per-interval", type=int, default=PHOTOS_PER_INTERVAL,
        help=f"Number of photos per day, default:{PHOTOS_PER_INTERVAL}")

    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Настройка логирования
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    start_hour = args.start_hour
    end_hour = args.end_hour
    photos_per_interval = args.photos_per_interval

    photo_interval_seconds = (
        ((end_hour - start_hour) * 60 * 60) // photos_per_interval)
    LOG.info("photo_interval_seconds:%s", photo_interval_seconds)
    LOG.info(
        "start_hour:%s end_hour:%s photos_per_interval:%s",
        start_hour, end_hour, photos_per_interval)

    try:
        while True:
            now = datetime.datetime.now()
            if is_time_to_shoot(now, start_hour, end_hour):
                LOG.info("Taking photo at %s", now.strftime("%H:%M:%S"))
                start_time = datetime.datetime(
                    year=now.year, month=now.month,
                    day=now.day, hour=start_hour
                )
                offset = (now - start_time).total_seconds()
                take_photo()
                # wait for the next interval
                sleep_period = (
                    1 - math.modf(offset / photo_interval_seconds)[0]
                ) * photo_interval_seconds + 0.1
                time.sleep(sleep_period)
            else:
                LOG.debug("Outside of shooting time, sleeping...")
                tomorrow = now + datetime.timedelta(days=1)
                next_start = tomorrow.replace(
                    hour=start_hour, minute=0, second=0, microsecond=0)
                sleep_seconds = (next_start - now).total_seconds()
                time.sleep(sleep_seconds)
    except KeyboardInterrupt:
        LOG.info("Script interrupted by user.")


if __name__ == "__main__":
    LOG.info("Daily photo script started.")
    main()
