import logging
from gps3.agps3threaded import AGPS3mechanism

class MyGPS(object):
    def __init__(self, host):
        self._agps_thread = AGPS3mechanism()  # Instantiate AGPS3 Mechanisms
        self._agps_thread.stream_data(host=host)
        self._agps_thread.run_thread()


    @property
    def coordinates(self):
        out = {"time": self._agps_thread.data_stream.time,
             "lat": self._agps_thread.data_stream.lat,
             "lng": self._agps_thread.data_stream.lon,
             "alt": self._agps_thread.data_stream.alt,
             }
        logging.warning(out)
        for k, v in out.items():
            if v == "n/a":
                out[k] = None

        return out


gps = MyGPS(GPSD_HOST)