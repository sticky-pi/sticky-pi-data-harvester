import os
import logging
import datetime
import glob
from sticky_pi_api.client import RemoteClient
from sticky_pi_api.image_parser import ImageParser
from sticky_pi_api.utils import string_to_datetime, datetime_to_string
import json
import dotenv


logging.getLogger().setLevel(logging.INFO)


SPI_API_CREDIENTIALS = os.environ["SPI_API_CREDIENTIALS"]
if os.path.exists(SPI_API_CREDIENTIALS):
    dotenv.load_dotenv(SPI_API_CREDIENTIALS)
else:
    logging.warning("No credential files. Will look in global variables")

SPI_API_HOSTNAME = os.environ["SPI_API_HOSTNAME"]
SPI_API_USERNAME = os.environ["SPI_API_USERNAME"]
SPI_API_PASSWORD = os.environ["SPI_API_PASSWORD"]
SPI_CLIENT_DIR = os.environ["SPI_CLIENT_DIR"]
IMG_ROOT_DIR = os.environ["IMG_ROOT_DIR"]



DELETE_OLDER_THAN = 30 # days

if __name__ == '__main__':


    client = RemoteClient(SPI_CLIENT_DIR,
                       SPI_API_HOSTNAME,
                       SPI_API_USERNAME, SPI_API_PASSWORD,
                       n_threads=1,
                       skip_on_error=True)

    all_images = [f for f in sorted(glob.glob(os.path.join(IMG_ROOT_DIR, '**', "*.jpg")))]

    for im in all_images:
        device, date_str, _ = os.path.basename(im).split('.')

        s = string_to_datetime(date_str)
        cut_off_date = datetime.datetime.now() - datetime.timedelta(days=DELETE_OLDER_THAN)
        if s >= cut_off_date:
            logging.info(f"Skipping recent image: {im}")
            continue
        try:
            im_info = ImageParser(im)
        except Exception as e:
            logging.warning(e)
            continue

        im_info["datetime"] = datetime_to_string(im_info["datetime"])
        server_image = client.get_images([im_info])

        if len(server_image) == 0:
            logging.warning(f"Image NOT on remote ({im})!")
        elif server_image[0]["md5"] != im_info["md5"]:
            logging.warning(f"Remote image has different md5 ({im})!")
        else:
            s_obj = os.stat(im)
            ghost =  {k: getattr(s_obj, k) for k in dir(s_obj) if k.startswith('st_')}
            ghost.update(dict(im_info))
            out = im + ".txt"
            with open(out, 'w') as o:
                o.write(json.dumps(ghost))
            logging.info(f"Removing old and synced image: {im}")
            os.remove(im)
            if os.path.exists(im + ".thumbnail"):
                os.remove(im + ".thumbnail")
