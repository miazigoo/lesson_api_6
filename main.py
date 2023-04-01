import os
from comics import (get_random_comics_url, fetch_comics_and_get_alt_filename)
from publish_in_VK import (get_wall_upload_server, save_wall_photo, wall_post_vk)


def main():
    comics_url = get_random_comics_url()
    alt, filename = fetch_comics_and_get_alt_filename(comics_url)
    photo, server, hash_vk = get_wall_upload_server(filename)

    owner_id, photo_id = save_wall_photo(photo, server, hash_vk)
    wall_post_vk(owner_id, photo_id, alt)
    os.remove(f"comics/{filename}")


if __name__ == '__main__':
    main()
