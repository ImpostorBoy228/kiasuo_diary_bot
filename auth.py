from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium import webdriver
import time
import json
import os
import logging

# В начале твоего файла
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fetcher")

TOKEN_PATH = 'bearer_token.json'
COOKIES_PATH = 'cookies.json'
KIASUO_URL = "https://pwa.kiasuo.ru/"

def save_token(token: str):
    with open(TOKEN_PATH, 'w', encoding='utf-8') as f:
        json.dump({"token": token}, f)

def load_token() -> str | None:
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("token")
    return None

def save_cookies(driver):
    cookies = driver.get_cookies()
    with open(COOKIES_PATH, 'w', encoding='utf-8') as f:
        json.dump(cookies, f)

def load_cookies() -> list | None:
    if os.path.exists(COOKIES_PATH):
        with open(COOKIES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_token_with_browser() -> str:
    opts = ChromeOptions()
    opts.add_argument("--start-maximized")
    # Укажи путь к бинарнику хрома, если он не стандартный (например, chromium-browser)
    opts.binary_location = "/usr/bin/chromium-browser"  # или "/usr/bin/google-chrome"

    # Можно включить опцию для headful режима, чтоб видеть окно браузера:
    # opts.add_argument("--headless=new")  # если хочешь без окна

    service = ChromeService()  # chromedriver должен быть в PATH

    driver = webdriver.Chrome(service=service, options=opts)
    driver.get(KIASUO_URL)

    print("🛑 Владыка, зайди вручную и нажми 'Войти через Госуслуги'.")

    while True:
        try:
            token = driver.execute_script("return window.localStorage.getItem('token');")
            if token:
                save_token(token)
                save_cookies(driver)
                driver.quit()
                logger.info("✅ Токен успешно призван, Владыка.")  # <-- добавил лог
                return token
        except Exception as e:
            logger.warning(f"⚠️ Ошибка при получении токена: {e}")
        time.sleep(1)
