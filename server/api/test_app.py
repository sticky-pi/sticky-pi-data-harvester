import time
import logging
import os
import requests
import glob
import json

DEVICE_ID = "5595c586"
ROOT_IMG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),'test_images')
pattern = os.path.join(ROOT_IMG_DIR, DEVICE_ID, "*.jpg")

def img_file_hash(path):
    stats = os.stat(path)
    #fixme. make a fast hash, e.g. using first and last bytes
    return f"hash-{stats.st_size}"

def get_device_status():
    status = {"version": "1.0",
                     "progress_skipping": 0, "progress_to_skip": 0, "progress_uploading": 0, "progress_to_upload": 0,
                     'in_transaction': 1}
    return status


HARVESTER_ROOT = "localhost:8082"
url_images_to_upload = f"http://{HARVESTER_ROOT}/images_to_upload/{DEVICE_ID}"
url_upload = f"http://{HARVESTER_ROOT}/upload_device_images/{DEVICE_ID}"
url_update_status = f"http://{HARVESTER_ROOT}/update_device_status/{DEVICE_ID}"
url_harvester_status = f"http://{HARVESTER_ROOT}/status/"


#fixme, here try to ping, first, then check response is OK!
response = requests.get(url_update_status)
assert response.status_code == 200, response
harvester_status = json.loads(response.content)

# update the pi metadata
new_metadata = {}
new_metadata.upate(harvester_status['gps_coordinates'])
new_metadata.upate({'time': harvester_status['time']})


device_status = get_device_status()
response = requests.post(url_update_status, json=device_status)


assert response.status_code == 200, response

files = {}
for f in sorted(glob.glob(pattern)):
    files[os.path.basename(f)] = img_file_hash(f)

response = requests.post(url_images_to_upload, json=files)
assert response.status_code == 200, response
image_status = json.loads(response.content)



for image, status in image_status.items():
    if status == "uploaded":
        device_status["progress_to_skip"] += 1
    else:
        device_status["progress_to_upload"] += 1

for image in sorted(image_status.keys()):
    image_path = os.path.join(ROOT_IMG_DIR, DEVICE_ID, image)
    print((image_path, image_status[image]))
    if image_status[image] != "uploaded":

        assert os.path.exists(image_path), f"Cannot find {image_path}"
        device_status["progress_uploading"] += 1
        # post = {'status': device_status, 'hash': img_file_hash(image_path)}
        # can also do multiple files in one payload...

        time.sleep(5)

        with open(image_path, 'rb') as f:

            payload = {'image': (image, f, 'application/octet-stream'),
                       'status': ('status', json.dumps(device_status), 'application/json'),
                       'hash': ('hash', json.dumps( img_file_hash(image_path)), 'application/json')
                       }

            response = requests.post(url_upload, files = payload)
            if response.status_code != 200:
                logging.error(response)
            # fixme here, retry if server cannot be reached
    else:
        device_status["progress_skipping"] += 1



# Formally finish transaction
device_status['in_transaction'] = 0
response = requests.post(url_update_status, json=device_status)
assert response.status_code == 200, response
