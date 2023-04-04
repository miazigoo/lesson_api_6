import os
import random
import requests
from pathlib import Path
from dotenv import load_dotenv
from os.path import (splitext, split)
from urllib.parse import (urlsplit, unquote)


def download_img(img_url, img_name):
    """ Download the comics """
    response = requests.get(img_url)
    response.raise_for_status()
    with open(f'{img_name}', 'wb') as file:
        file.write(response.content)


def get_filename_and_ext(img_url):
    """Getting the link address and extension"""
    url_address = urlsplit(img_url).path
    encoding_url = unquote(url_address)
    filename = split(encoding_url)[-1]
    extension = splitext(filename)[-1]
    return filename, extension


def get_random_comic_url():
    """ Получаем рандомный комикс """
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    all_comics_num = response.json()['num']
    random_comics_num = random.randint(1, (all_comics_num + 1))
    comic_url = f'https://xkcd.com/{random_comics_num}/info.0.json'
    return comic_url


def get_alt_filename_url(comic_url):
    """ Получаем запись к комиксу и его название """
    response = requests.get(comic_url)
    response.raise_for_status()
    comic = response.json()
    img_url = comic['img']
    alt = comic['alt']
    filename, _ = get_filename_and_ext(img_url)
    return alt, filename, img_url


def fetch_comic(img_url, filename):
    """ Скачиваем комикс """
    download_img(img_url, filename)
    return "Download comic Success"


def upload_an_image_to_the_server(filename, access_token, group_id, vk_api_version):
    """ Загружаем комикс на сервер ВК """
    url = f'https://api.vk.com/method/photos.getWallUploadServer?'
    params = {
        'access_token': access_token,
        'group_id': group_id,
        'v': vk_api_version,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']

    with open(f'{filename}', 'rb') as file:
        files = {
            'photo': file,
        }
        up_response = requests.post(upload_url, files=files)
        up_response.raise_for_status()
    upload_photo = up_response.json()
    photo = upload_photo['photo']
    server = upload_photo['server']
    hash_vk = upload_photo['hash']
    return photo, server, hash_vk


def save_wall_photo(photo, server, vk_hash, access_token, group_id, vk_api_version):
    """ Сохраняем комикс на сервере """
    url = f'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'access_token': access_token,
        'group_id': group_id,
        'photo': photo,
        'server': server,
        'hash': vk_hash,
        'v': vk_api_version,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    photo_owner = response.json()['response'][0]
    owner_id = photo_owner['owner_id']
    photo_id = photo_owner['id']
    return owner_id, photo_id


def publish_wall_post_vk(owner_id, photo_id, alt, access_token, group_id, vk_api_version):
    """ Публикуем на стене группы ВК """
    url = f'https://api.vk.com/method/wall.post'
    attachments = f'photo{owner_id}_{photo_id}'
    from_group = 1
    params = {
        'access_token': access_token,
        'owner_id': f'-{group_id}',
        'from_group': from_group,
        'attachments': attachments,
        'message': alt,
        'v': vk_api_version,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()


def main():
    load_dotenv()
    access_token = os.environ['VK_ACCESS_TOKEN']
    group_id = os.environ['VK_GROUP_ID']
    vk_api_version = 5.131
    comic_url = get_random_comic_url()
    alt, filename, img_url = get_alt_filename_url(comic_url)
    fetch_comic(img_url, filename)
    try:
        photo, server, vk_hash = upload_an_image_to_the_server(filename, access_token, group_id, vk_api_version)
        owner_id, photo_id = save_wall_photo(photo, server, vk_hash, access_token, group_id, vk_api_version)
        publish_wall_post_vk(owner_id, photo_id, alt, access_token, group_id, vk_api_version)
    finally:
        file = Path(f"{filename}")
        os.remove(file)


if __name__ == '__main__':
    main()
