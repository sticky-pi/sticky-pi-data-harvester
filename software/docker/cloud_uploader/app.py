import logging
import threading
import os
import glob
import time
import io
import dotenv

from flask import Flask, jsonify
from sticky_pi_api.client import RemoteClient, RemoteAPIException


app = Flask(__name__)

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
#
stream = io.StringIO()
log = logging.getLogger()
logging.getLogger().setLevel(logging.INFO)
handler = logging.StreamHandler(stream)
log.addHandler(handler)


class CloudUploadDaemon(threading.Thread):
    def __init__(self, img_root_dir, client_dir, host, username, password):
        self._img_root_dir = img_root_dir
        self._client_dir = client_dir
        self._host = host
        self._username = username
        self._password = password
        self._connection_status = "unreachable"
        self._upload_status = "pending"
        super().__init__()

    @property
    def connection_status(self):
        return self._connection_status

    @property
    def upload_status(self):
        return self._upload_status

    def _set_connection_status(self):
        response = os.system(f"ping -c 3 %s > /dev/null" % self._host)
        if response == 0:
            self._connection_status = "connected"
        else:
            self._connection_status = "unreachable"

    def run(self):
        last_most_recent_file_timestamp = 0
        all_files_uploaded = False
        while True:
            self._set_connection_status()
            images_to_sync = [g for g in glob.glob(os.path.join(self._img_root_dir, '**', '*.jpg'))]
            if len(images_to_sync) == 0:
                time.sleep(10)
                continue
            most_recent_file_timestamp = max([os.path.getmtime(f) for f in images_to_sync])
            # print (last_most_recent_file_timestamp, most_recent_file_timestamp)
            if last_most_recent_file_timestamp != most_recent_file_timestamp:
                all_files_uploaded = False
                self._upload_status = "pending"
            else:
                self._upload_status = "done"
            if all_files_uploaded or self._connection_status != "connected":
                time.sleep(10)
                continue

            self._upload_status = "uploading"
            try:
                stream.truncate(0)
                stream.seek(0)
                cli = RemoteClient(self._client_dir, self._host, self._username, self._password, n_threads=1, skip_on_error=True)
                cli.put_images(images_to_sync)
                last_most_recent_file_timestamp = most_recent_file_timestamp
            except RemoteAPIException as e:
                self._upload_status = "upload error"
                logging.error(e)
                print(e)
            except Exception as e:
                self._upload_status = "unknown error"
                logging.error(e)
                print(e)
            all_files_uploaded = True
            time.sleep(10)



cloud_uploader = CloudUploadDaemon(IMG_ROOT_DIR, SPI_CLIENT_DIR, SPI_API_HOSTNAME, SPI_API_USERNAME, SPI_API_PASSWORD)
cloud_uploader.start()


@app.route('/', methods=['GET'])
def index():
    if not cloud_uploader.is_alive():
        logging.error("Uploader Thread dead! stopping")
        exit(1)
    logs = stream.getvalue()
    if not logs:
        logs = None
    # logger?
    out = {"logs": logs,
           "connection_status": cloud_uploader.connection_status,
           "upload_status": cloud_uploader.upload_status}
    return jsonify(out)
