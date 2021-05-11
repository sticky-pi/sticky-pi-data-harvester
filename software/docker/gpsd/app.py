from flask import Flask, jsonify
import iso8601
from gps3.agps3threaded import AGPS3mechanism
import subprocess
import logging
import threading
import time
import os


app = Flask(__name__)

GPS_DEVICE = os.environ["GPS_DEVICE"]
assert os.path.exists(GPS_DEVICE), f"No GPS device {GPS_DEVICE}"

class MyGPS(threading.Thread):
    _persist_time = 10
    _kill_no_gps_data = 10  # s

    def __init__(self):
        self._last_coordinates = {"time": None,
                                  "lat": None,
                                  "lng": None,
                                  "alt": None,
                                  }
        self._last_gps_record = (time.time(), time.time())  # (OS, GPS)

        # self._agps_thread = self._agps_thread_instance()
        super().__init__()

    def run(self):
        gpsd = subprocess.Popen(["gpsd", "-N", "-n", "-G", "-D3", "-S", "2947", "-F", "/var/run/gpsd.sock", GPS_DEVICE])
        time.sleep(3)
        agps_thread = AGPS3mechanism()  # Instantiate AGPS3 Mechanisms
        agps_thread.stream_data()
        agps_thread.run_thread()

        while True:
            if gpsd.poll() is not None:
                logging.error(f"GPSD has stopped. KILLING process.")
                try:
                    gpsd.terminate()
                finally:
                    os._exit(1)

            now = time.time()
            out = {"time": agps_thread.data_stream.time,
                   "lat": agps_thread.data_stream.lat,
                   "lng": agps_thread.data_stream.lon,
                   "alt": agps_thread.data_stream.alt,
                   }

            logging.warning("Raw GPS out")
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
                    try:
                        self._gpsd.terminate()
                    finally:
                        os._exit(1)
                else:
                    logging.warning("No valid GPS record")

            valid_last_coords = self._last_coordinates and self._last_coordinates["time"] and (
                        now - self._last_coordinates["time"]) < self._persist_time

            for k, v in out.items():
                if out[k] is None and valid_last_coords:
                    out[k] = self._last_coordinates[k]
            self._last_coordinates = out
            time.sleep(1)

    @property
    def coordinates(self):
        return self._last_coordinates


class MockGPS(MyGPS):

    def _agps_thread_instance(self):
        class MockApgs(object):
            @property
            def data_stream(self):
                import collections
                import datetime
                Out = collections.namedtuple("Coordinates", ["time", "lat", "lon", "alt"])
                return Out(datetime.datetime.now().isoformat(), 49.26, -123.23, 12)

        return MockApgs()


if int(os.environ["MOCK_GPS"]) == 1:
    gps = MockGPS()
else:
    gps = MyGPS()

gps.start()


@app.route('/', methods=['GET'])
def index():
    if not gps.is_alive():
        logging.error("GPS Thread dead! stopping")
        exit(1)
    return jsonify(gps.coordinates)
