import requests
import json
import os
import time
import random
from dotenv import dotenv_values
from pathlib import Path
from datetime import datetime

from utils.py_logger import get_logger

logger = get_logger(__name__)
config = dotenv_values(".env")
PROXY_API_KEY = config.get("PROXY_API_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent
proxy_storage = 'utils/proxy_list.json'


def load_proxies():
    """Функція завантаження проксі по АРІ"""
    response = requests.get(
        "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100",
        headers={"Authorization": PROXY_API_KEY}
    )
    if response.status_code == 200:
        logger.info(f"Proxies was upload")
        proxies = response.json()
        with open(f"{BASE_DIR.joinpath(proxy_storage)}", 'w') as file:
            json.dump(proxies, file, indent=4, ensure_ascii=False)
            logger.info(f"Proxies was saved")


def get_random_proxy():
    """Функція перевірки та отримання валідного proxy"""
    delta_hours = 2
    if os.path.exists(proxy_storage):
        time_file_created = datetime.fromtimestamp(os.path.getmtime(proxy_storage))
        delta_seconds = (datetime.now() - time_file_created).total_seconds()
        delta_hours = delta_seconds / 3600
    if delta_hours >= 2:  # якщо файл старий, понад 24 годин - то оновлюємо проксі
        load_proxies()
        time.sleep(1)
        return get_random_proxy()
    else:
        with open(f"{BASE_DIR.joinpath(proxy_storage)}") as file:
            proxies = json.load(file)
            results = proxies.get("results")
            if results:
                random.shuffle(results)
                for item in results:
                    proxy_address = item.get("proxy_address")
                    port = item.get("port")
                    username = item.get("username")
                    password = item.get("password")
                    return {"PROXY_SERVER": f"{proxy_address}:{port}", "PROXY_USERNAME": username,
                            "PROXY_PASSWORD": password}
