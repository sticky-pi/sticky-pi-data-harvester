import logging
from gps3.agps3threaded import AGPS3mechanism

import shutil
import glob
import logging
import json
import os
import redis
from typing import Tuple, Dict
import time

def img_file_hash(path):
    stats = os.stat(path)
    #fixme. make a fast hash, e.g. using first and last bytes
    return f"hash-{stats.st_size}"


class Harvester(object):
    _gps_coord_persistence_t = 120  # if gps reads fail, we use past data as long as it is not older then this var

    def __init__(self, img_root_dir, redis_host, gps):
        self._gps = gps
        self._devices_db = redis.Redis(redis_host)
        # self._devices = {}  # the detected devices. id:str -> {images -> {name -> md5},status -> }
        self._local_images = {}
        self._img_root_dir = img_root_dir
        os.makedirs(self._img_root_dir, exist_ok=True)


    def update_device_status(self, id, status):
        id = id.encode("ascii")
        self._devices_db.set(id, json.dumps(status))

    def upload_device_image(self, id, file,  status, hash):
        filename = file.filename

        assert id == filename.split('.')[0]
        target = os.path.join(self._img_root_dir, id, filename)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        tmp = target + "-tmp"
        try:
            file.save(tmp)
            assert hash == img_file_hash(tmp), "Uploaded filed does not match its hash"
        except Exception as e:
            logging.error(e)
            os.remove(tmp)
            raise e
        os.rename(tmp, target)

        self.update_device_status(id, status)
        out = {}

        return out

    def images_to_upload(self, id: str,
                             images: Dict[str, str]  # name -> hash/checksum/...
                             ) -> Dict[str, str]:
        """
        for the device to send the list of images and checksums and retrieves the files to upload
        :param images:
        :return:
        """

        out = {}
        n_missing_on_remote, n_checksum_differs, n_uploaded = 0, 0, 0

        for device_im_name, device_im_hash in images.items():
            local_file = os.path.join(self._img_root_dir, id, device_im_name)
            if not os.path.exists(local_file):
                im_status = "missing_on_remote"
                n_missing_on_remote += 1
            elif img_file_hash(local_file) != device_im_hash:
                im_status = "checksum_differs"
                n_checksum_differs += 1
            else:
                im_status = "uploaded"
                n_uploaded += 1
            out[device_im_name] = im_status
        return out

    # @property
    # def devices(self) -> Dict[str, Dict[str, Dict]]:
    #     return self._devices

    @property
    def disk_info(self) -> Dict[str, float]:
        total, used, free = shutil.disk_usage(self._img_root_dir)
        return {"total": total,
                "used": used,
                "free": free}

    @property
    def n_image_files(self) -> int:

        return len(glob.glob(os.path.join(self._img_root_dir, '**', '*.jpg')))

    @property
    def devices(self):
        out = []
        for key in self._devices_db.scan_iter():
            d = json.loads(self._devices_db.get(key).decode('ascii'))
            d["id"] = key.decode("ascii")
            out.append(d)
        return out


    @property
    def time(self) -> float:
        return time.time()

    @property
    def gps_coordinates(self) -> Dict:
        return self._gps.coordinates

    @property
    def ip_address(self) -> str:
        return "0.0.0.0"# todo


class DummyHarvester(Harvester):
    pass


class MyGPS(object):
    def __init__(self, host):
        self._agps_thread = AGPS3mechanism()  # Instantiate AGPS3 Mechanisms
        self._agps_thread.stream_data(host=host)
        self._agps_thread.run_thread()

    @property
    def coordinates(self):
        logging.warning(self._agps_thread.data_stream)
        out = {"time": self._agps_thread.data_stream.time,
             "lat": self._agps_thread.data_stream.lat,
             "lng": self._agps_thread.data_stream.lon,
             "alt": self._agps_thread.data_stream.alt,
             }
        # stop
        for k, v in out.items():
            if v == "n/a":
                out[k] = None

        return out


g = MyGPS("harvester_gpsd")
h = Harvester("/tmp", "")