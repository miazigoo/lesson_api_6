import os
from dotenv import load_dotenv
import requests


load_dotenv()
""" CONSTANTS """
VK_ACCESS_TOKEN = os.environ['VK_ACCESS_TOKEN']
VK_GROUP_ID = os.environ['VK_GROUP_ID']
VERSION_VK_API = 5.131


def get_wall_upload_server(filename):
    """ Загружаем комикс на сервер ВК """
    url = f'https://api.vk.com/method/photos.getWallUploadServer?'
    params = {
        'access_token': VK_ACCESS_TOKEN,
        'group_id': VK_GROUP_ID,
        'v': VERSION_VK_API,
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


def save_wall_photo(photo, server, hash_vk):
    """ Сохраняем комикс на сервере """
    url = f'https://api.vk.com/method/photos.saveWallPhoto'
    params = {
        'access_token': VK_ACCESS_TOKEN,
        'group_id': VK_GROUP_ID,
        'photo': photo,
        'server': server,
        'hash': hash_vk,
        'v': VERSION_VK_API,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    upload_vk = response.json()['response'][0]
    owner_id = upload_vk['owner_id']
    photo_id = upload_vk['id']
    return owner_id, photo_id


def wall_post_vk(owner_id, photo_id, alt):
    """ Публикуем на стене группы ВК """
    url = f'https://api.vk.com/method/wall.post'
    attachments = f'photo{owner_id}_{photo_id}'
    from_group = 1
    params = {
        'access_token': VK_ACCESS_TOKEN,
        'owner_id': f'-{VK_GROUP_ID}',
        'from_group': from_group,
        'attachments': attachments,
        'message': alt,
        'v': VERSION_VK_API,
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
