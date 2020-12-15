import requests
import os
from dotenv import load_dotenv
import random
import argparse
from pathlib import Path


def download_images(url, filename):
    response = requests.get(url, verify=False)
    response.raise_for_status()
    image_path = Path.cwd() / filename
    with open(image_path, 'wb') as file:
        file.write(response.content)


def download_comic_img():
    url = "http://xkcd.com/614/info.0.json"
    response = requests.get(url)
    comic_info = response.json()
    random_id = random.randint(0, comic_info["num"])
    random_img_url = f"http://xkcd.com/{random_id}/info.0.json"
    response = requests.get(random_img_url)
    img_irl = response.json()['img']
    filename = f"comic{random_id}{os.path.splitext(img_irl)[1]}"
    download_images(img_irl, filename)
    return comic_info, filename


def get_upload_url(group_id, token):
    url1 = "https://api.vk.com/method/photos.getWallUploadServer"
    payload = {"group_id": group_id,
               "access_token": token,
               "v": 5.126}
    response = requests.post(url1, params=payload)
    upload_url = response.json()['response']['upload_url']
    return upload_url


def get_img_info(group_id, upload_info, token):
    save_url = "https://api.vk.com/method/photos.saveWallPhoto"
    payload = {"group_id": group_id,
               "photo": upload_info["photo"],
               "server": upload_info["server"],
               "hash": upload_info["hash"],
               "access_token": token,
               "v": 5.126}
    response = requests.post(save_url, params=payload)
    img_info = response.json()["response"][0]
    return img_info


def publishes_comic(group_id, img_info, comic_info, token):
    publication_url = "https://api.vk.com/method/wall.post"
    payload = {"owner_id": int(f"-{group_id}"),
               "from_group": 1,
               "attachments": f'photo{img_info["owner_id"]}_{img_info["id"]}',
               "message": comic_info["alt"],
               "access_token": token,
               "v": 5.126}
    requests.post(publication_url, params=payload)


def main():
    parser = argparse.ArgumentParser(description='Публикует комикс в группу ВКонтакте')
    parser.add_argument('--group_id', help='ID вашей группы ВК')
    parser.add_argument('--token', help='Ваш access_token')
    args = parser.parse_args()
    load_dotenv()
    group_id = args.group_id or os.environ["VK_GROUP_ID"]
    token = args.token or os.environ["VK_TOKEN"]
    comic_info, filename = download_comic_img()
    try:
        upload_url = get_upload_url(group_id, token)
        with open(filename, 'rb') as file:
            files = {'photo': file}
            response = requests.post(upload_url, files=files)
            upload_info = response.json()
        img_info = get_img_info(group_id, upload_info, token)
        publishes_comic(group_id, img_info, comic_info, token)
    finally:
        path_to_comic = Path.cwd() / filename
        Path.unlink(path_to_comic)


if __name__ == '__main__':
    main()


