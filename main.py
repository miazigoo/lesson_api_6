import os
import random
import requests
from pathlib import Path
from dotenv import load_dotenv
from os.path import (splitext, split)
from urllib.parse import (urlsplit, unquote)


def download_img(img_url, img_name, imgs_path):
    """ Download the comics """
    img_path = Path(imgs_path)
    img_path.mkdir(parents=True, exist_ok=True)
    response = requests.get(img_url)
    response.raise_for_status()
    with open(f'{img_path}/{img_name}', 'wb') as file:
        file.write(response.content)


def get_filename_and_ext(img_url):
    """Getting the link address and extension"""
    url_address = urlsplit(img_url).path
    encoding_url = unquote(url_address)
    filename = split(encoding_url)[-1]
    extension = splitext(filename)[-1]
    return filename, extension


def get_random_comics_url():
    """ Получаем рандомный комикс """
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    all_comics_num = response.json()['num']
    random_comics_num = random.randint(1, (all_comics_num + 1))
    comics_url = f'https://xkcd.com/{random_comics_num}/info.0.json'
    return comics_url


def fetch_comics_and_get_alt_filename(url):
    """ Скачиваем комикс, получаем запись к комиксу и название """
    response = requests.get(url)
    response.raise_for_status()
    comics = response.json()

    img_url = comics['img']
    alt = comics['alt']
    filename, _ = get_filename_and_ext(img_url)
    comics_path = 'comics'
    download_img(img_url, filename, comics_path)
    return alt, filename


def get_wall_upload_server(filename, access_token, group_id, vk_api_version):
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

    with open(f'comics/{filename}', 'rb') as file:
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


def save_wall_photo(photo, server, hash_vk, access_token, group_id, vk_api_version):
    """ Сохраняем комикс на сервере """
    url = f'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'access_token': access_token,
        'group_id': group_id,
        'photo': photo,
        'server': server,
        'hash': hash_vk,
        'v': vk_api_version,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    upload_vk = response.json()['response'][0]
    owner_id = upload_vk['owner_id']
    photo_id = upload_vk['id']
    return owner_id, photo_id


def wall_post_vk(owner_id, photo_id, alt, access_token, group_id, vk_api_version):
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
    comics_url = get_random_comics_url()
    alt, filename = fetch_comics_and_get_alt_filename(comics_url)
    photo, server, hash_vk = get_wall_upload_server(filename, access_token, group_id, vk_api_version)

    owner_id, photo_id = save_wall_photo(photo, server, hash_vk, access_token, group_id, vk_api_version)
    wall_post_vk(owner_id, photo_id, alt, access_token, group_id, vk_api_version)
    os.remove(f"comics/{filename}")


if __name__ == '__main__':
    main()
