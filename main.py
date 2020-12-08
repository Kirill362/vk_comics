import requests
import os
from dotenv import load_dotenv
import random


def download_images(url, filename, images_folder):
  response = requests.get(url, verify=False)
  response.raise_for_status()
  image_path = f"{images_folder}/{filename}"
  with open(image_path, 'wb') as file:
    file.write(response.content)


load_dotenv()
client_id = os.environ["CLIENT_ID"]
token = os.environ["TOKEN"]
url = "http://xkcd.com/614/info.0.json"
response = requests.get(url)
response.raise_for_status()
comic_info = response.json()
random_id = random.randint(0, comic_info["num"])
random_img_url = f"http://xkcd.com/{random_id}/info.0.json"
response = requests.get(random_img_url)
response.raise_for_status()
img_irl = response.json()['img']
filename = f"comic{random_id}{os.path.splitext(img_irl)[1]}"
download_images(img_irl, filename, ".")

url1 = "https://api.vk.com/method/photos.getWallUploadServer"
payload = {"group_id": 200790193,
           "access_token": token,
           "v": 5.126}
response = requests.post(url1, params=payload)
response.raise_for_status()
upload_url = response.json()['response']['upload_url']

with open(filename, 'rb') as file:
    files = {
        'photo': file,
    }
    response = requests.post(upload_url, files=files)
    response.raise_for_status()
    upload_info = response.json()

save_url = "https://api.vk.com/method/photos.saveWallPhoto"
payload = {"group_id": 200790193,
           "photo": upload_info["photo"],
           "server": upload_info["server"],
           "hash": upload_info["hash"],
           "access_token": token,
           "v": 5.126}
response = requests.post(save_url, params=payload)
response.raise_for_status()
img_info = response.json()

publication_url = "https://api.vk.com/method/wall.post"
payload = {"owner_id": -200790193,
           "from_group": 1,
           "attachments": f'photo{img_info["response"][0]["owner_id"]}_{img_info["response"][0]["id"]}',
           "message": comic_info["alt"],
           "access_token": token,
           "v": 5.126}
response = requests.post(publication_url, params=payload)
response.raise_for_status()

os.remove(f"./{filename}")


