import requests
from pathlib import Path


def download_img(img_url, img_name, imgs_path):
    """ Download the comics """
    img_path = Path(imgs_path)
    img_path.mkdir(parents=True, exist_ok=True)
    response = requests.get(img_url)
    response.raise_for_status()
    with open(f'{img_path}/{img_name}', 'wb') as file:
        file.write(response.content)