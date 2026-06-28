import json
import requests
import urllib.parse

CAT_API = "https://cataas.com"
YANDEX_API = "https://cloud-api.yandex.net/v1/disk/resources"


def get_headers(token):
    return {"Authorization": f"OAuth {token}"}


def get_cat_image(text):
    encoded_text = urllib.parse.quote(text)
    url = f"{CAT_API}/cat/says/{encoded_text}?width=400"
    return url


def create_folder(token, folder_name):
    response = requests.put(
        YANDEX_API,
        headers=get_headers(token),
        params={"path": f"disk:/{folder_name}"}
    )

    if response.status_code not in [201, 409]:
        print("Ошибка создания папки:", response.text)


def upload_from_url(token, file_url, disk_path):
    response = requests.post(
        f"{YANDEX_API}/upload",
        headers=get_headers(token),
        params={
            "path": disk_path,
            "url": file_url,
            "overwrite": "true"
        }
    )

    if response.status_code != 202:
        print("Ошибка загрузки файла:", response.text)


def upload_json(token, data, disk_path):
    file_name = "result.json"

    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    response = requests.get(
        f"{YANDEX_API}/upload",
        headers=get_headers(token),
        params={
            "path": disk_path,
            "overwrite": "true"
        }
    )

    href = response.json()["href"]

    with open(file_name, "rb") as file:
        requests.put(href, files={"file": file})


def get_file_name(text, image_url):
    original_name = image_url.split("/")[-1]
    safe_text = "".join(c for c in text if c.isalnum() or c in " ._-")
    return f"{safe_text}_{original_name}"


def main():
    text = input("Введите текст для картинки кошки: ").strip()
    token = input("Введите токен Яндекс.Диска: ")

    if not text:
        print("Текст не может быть пустым!")
        return

    group_name = "QAMIDPY-134"

    folder_path = f"disk:/{group_name}"
    create_folder(token, group_name)

    result = []

    print("Загружается:", text)

    image_url = get_cat_image(text)
    file_name = get_file_name(text, image_url)
    disk_path = f"{folder_path}/{file_name}"

    upload_from_url(token, image_url, disk_path)

    result.append({
        "text": text,
        "file_name": file_name,
        "url": image_url,
        "yandex_path": disk_path
    })

    upload_json(token, result, f"{folder_path}/result.json")

    print("Готово!")


main()