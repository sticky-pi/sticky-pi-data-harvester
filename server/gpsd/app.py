from flask import Flask, jsonify
import iso8601
from gps3.agps3threaded import AGPS3mechanism
import subprocess
import time
import logging

gpsd = subprocess.call(["gpsd", "-n", "-G", "-D3", "-S", "2947", "-F", "/var/run/gpsd.sock", "/dev/ttyUSB0"])
assert gpsd == 0
# process is not running
# if gpsd.poll() is  not None:
#     logging.error("GPSd not running!!")
#     exit(1)

app = Flask(__name__)

class MyGPS(object):
    _persist_time = 60
    _kill_no_gps_data = 300 #s
    def __init__(self):
        self._agps_thread = AGPS3mechanism()  # Instantiate AGPS3 Mechanisms
        self._agps_thread.stream_data()
        self._agps_thread.run_thread()
        self._last_coordinates = {}
        self._last_gps_record = (time.time(), time.time()) # (OS, GPS)

    @property
    def coordinates(self):
        now = time.time()
        # todo kill gpsd if no data!
        out = {"time": self._agps_thread.data_stream.time,
             "lat": self._agps_thread.data_stream.lat,
             "lng": self._agps_thread.data_stream.lon,
             "alt": self._agps_thread.data_stream.alt,
             }

        logging.warning(out)
        for k, v in out.items():
            if v == "n/a":
                out[k] = None

        if out["time"]:
            out["time"] = iso8601.parse_date(out["time"]).timestamp()

        # a valid record
        if out["time"] and out["time"] > self._last_gps_record[1]:
            self._last_gps_record = (now, out["time"])
        # frozen gpsd
        else:
            if (now - self._last_gps_record[0]) > self._kill_no_gps_data:
                logging.error(f"No GPS data in {self._kill_no_gps_data}s. KILLING process.")
                exit(1)
            else:
                logging.warning("No valid GPS record")

        valid_last_coords = self._last_coordinates and self._last_coordinates["time"] and (now - self._last_coordinates["time"]) < self._persist_time
        for k, v in out.items():
            if out[k] is None and valid_last_coords:
                out[k] = self._last_coordinates[k]

        self._last_coordinates = out
        return out


gps = MyGPS()

@app.route('/', methods=['GET'])
def index():
   return jsonify(gps.coordinates)
