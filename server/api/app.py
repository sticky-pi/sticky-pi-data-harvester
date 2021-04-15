from flask import Flask, jsonify
from flask import request
import logging
import json
import time

from harvester_tools.harvester import Harvester
# TODO
# https://wiki.archlinux.org/index.php/Network_Time_Protocol_daemon#Using_ntpd_with_GPS

IMG_ROOT_DIR = "/sticky_pi/"
REDIS_HOST = 'redis'
GPS_HOST = 'harvester_gpsd'
app = Flask(__name__)
harvester = Harvester(IMG_ROOT_DIR, REDIS_HOST, GPS_HOST)

@app.route('/', methods=['GET'])
def index():
    return app.send_static_file("index.html")


@app.route('/status', methods=['GET'])
def status():
    out = {
        'time': harvester.time,
        'gps_coordinates': harvester.gps_coordinates,
        'disk_info': harvester.disk_info,
        'devices': harvester.devices,
        'n_local_images': harvester.n_image_files,
    }
    logging.warning(out)
    return jsonify(out)


@app.route('/images_to_upload/<id>', methods=['POST'])
def images_to_upload(id: str):
    data = request.get_json()
    out = harvester.images_to_upload(id, data)
    return jsonify(out)


@app.route('/update_device_status/<id>', methods=['POST'])
def update_device_status(id: str):
    status = request.get_json()
    assert status
    # here get time of update
    # ip of client
    status["ip"] = request.remote_addr
    status["updated_time"] = time.time()

    harvester.update_device_status(id, status)
    return jsonify({})

@app.route('/upload_device_images/<id>', methods=['POST'])
def upload_device_images(id: str):
    files = request.files
    assert len(files) == 3
    file = files["image"]
    status = json.load(files["status"])
    hash = json.load(files["hash"])

    status["ip"] = request.remote_addr
    status["updated_time"] = time.time()
    out = harvester.upload_device_image(id, file, status, hash)
    return jsonify(out)
