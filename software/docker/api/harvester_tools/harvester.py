import datetime
import shutil
import glob
import logging
import json
import os
import redis
from typing import Tuple, Dict
import time
import requests
from PIL import Image

def img_file_hash(path):
    stats = os.stat(path)
    #fixme. make a fast hash, e.g. using first and last bytes
    return f"hash-{stats.st_size}"


class Harvester(object):
    _gps_coord_persistence_t = 120  # if gps reads fail, we use past data as long as it is not older then this var
    _thumbnail_size = 128, 128
    def __init__(self, img_root_dir, redis_host, gps_host):
        self._gps_host = gps_host
        self._devices_db = redis.Redis(redis_host)

        for d in self.devices:
            if "in_transaction" in d and d["in_transaction"] == 1:
                d["in_transaction"] = 0
                self.update_device_status(d["id"], d)

        self._local_images = {}
        self._img_root_dir = img_root_dir
        os.makedirs(self._img_root_dir, exist_ok=True)


    def update_device_status(self, id, status):
        id = id.encode("ascii")
        # if redis dict has keys that are not in the provided status, we recycle old values
        if self._devices_db.exists(id):
            d = json.loads(self._devices_db.get(id).decode('ascii'))
            d.update(status)
            status = d
        self._devices_db.set(id, json.dumps(status))

    def upload_device_image(self, id, file,  status, hash):
        filename = file.filename
        im_id, im_datetime, _ = filename.split('.')
        assert id == im_id
        target = os.path.join(self._img_root_dir, id, filename)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        tmp = target + "-tmp"
        try:
            file.save(tmp)
            assert hash == img_file_hash(tmp), "Uploaded files does not match its hash"
        except Exception as e:
            logging.error(e)
            os.remove(tmp)
            raise e
        os.rename(tmp, target)
        with Image.open(target) as im:
            im.thumbnail(self._thumbnail_size)
            im.save(target + ".thumbnail", "JPEG")

        status["last_image_path"] = os.path.relpath(target,self._img_root_dir)
        status["last_image_thumbnail_path"] = os.path.relpath(target + ".thumbnail" ,self._img_root_dir)
        status["last_image_timestamp"] = datetime.datetime.strptime(im_datetime, '%Y-%m-%d_%H-%M-%S').timestamp()
        self.update_device_status(id, status)
        out = {}

        return out

    def images_to_upload(self, id: str,
                             images: Dict[str, str]  # name -> hash/checksum/...
                             ) -> Dict[str, str]:
        """
        For the device to send the list of images and checksums and retrieves the files to upload
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
        out = [o for o in sorted(out, key = lambda x : x["updated_time"])]

        return out


    @property
    def time(self) -> float:
        return time.time()

    @property
    def gps_coordinates(self) -> Dict:
        try:
            resp = requests.get("http://" + self._gps_host, timeout=0.2)
            if resp.status_code == 200:
                out = json.loads(resp.content)
                assert "lat" in out
            else:
                #fixme should be tolerant here
                raise Exception("GPS server down!")
        except Exception as e:
            logging.error(e)
            out = {"alt": None, "lat": None, "lng": None, "time": None}
        return out

    @property
    def ip_address(self) -> str:
        return "0.0.0.0"# todo


class DummyHarvester(Harvester):
    pass
