import random
import requests
from download import download_img
from get_filename_and_ext import get_filename_and_ext


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
