import asyncio
import random
import time
from dotenv import dotenv_values

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent

from services.proxy_service import get_random_proxy
from utils.py_logger import get_logger

logger = get_logger(__name__)
config = dotenv_values(".env")

EMAIL_NBU = config.get("EMAIL_NBU")
PASSWORD_NBU = config.get("PASSWORD_NBU")
EMAIL_NBU_MASHA = config.get("EMAIL_NBU_MASHA")
PASSWORD_NBU_MASHA = config.get("PASSWORD_NBU_MASHA")

# user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#               'Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0')

# Задаємо посилання на сторінку login
# link = "https://coins.bank.gov.ua/login.php"


class SeleniumRunner:

    def __init__(self, email, password, coin_name, browser='chrome'):
        self.link = "https://coins.bank.gov.ua/login.php"
        self.email = email
        self.password = password
        self.coin_name = coin_name
        self.driver = None
        self.fake_useragent = None
        self.browser = browser

    @staticmethod
    def fake_user():
        ua = UserAgent()
        user_agent = ua.random
        print(user_agent)
        return user_agent

    def start_driver(self):
        if self.browser == 'chrome':
            chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_argument("--incognito")
            self.fake_useragent = self.fake_user()  # Генеруємо новий User-Agent
            chrome_options.add_argument(f'user-agent={self.fake_useragent}')
            self.driver = webdriver.Chrome(options=chrome_options)
        elif self.browser == 'firefox':
            firefox_options = webdriver.FirefoxOptions()
            # firefox_options.add_argument("--private")
            self.fake_useragent = self.fake_user()  # Генеруємо новий User-Agent
            firefox_options.add_argument(f'user-agent={self.fake_useragent}')
            self.driver = webdriver.Firefox(options=firefox_options)
        else:
            raise ValueError("Unsupported browser type")

    def login(self):
        try:
            self.driver.get(self.link)
            time.sleep(random.uniform(2, 4))
            actions = ActionChains(self.driver)
            time.sleep(random.uniform(2, 5))
            login_button = self.driver.find_element(By.CLASS_NAME, "small-menu-cabinet")

            time.sleep(random.uniform(2, 5))
            actions.move_to_element(login_button).click().perform()

            email_input = self.driver.find_element("name", "email_address")
            email_input.send_keys(self.email)

            password_input = self.driver.find_element("name", "password")
            password_input.send_keys(self.password)

            time.sleep(random.uniform(1, 3))
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(text(), 'Увійти')]"))
            )
            login_button.click()
            logger.info(f"{self.browser} | {self.email} ==> Авторизація пройшла успішно!", extra={'custom_color': True})
        except Exception as err:
            logger.error(f"{self.browser} | {self.email} ==> Помилка авторизації: {err}")

    def search(self):
        try:

            """Логіка натискання мишкою"""
            # Створюємо екземпляр ActionChains, пов'язаний з драйвером
            actions = ActionChains(self.driver)
            time.sleep(random.uniform(2, 5))

            search_button = self.driver.find_element(By.CLASS_NAME, "small-menu-search")
            time.sleep(random.uniform(2, 5))
            actions.move_to_element(search_button).click().perform()

            search_input = self.driver.find_element(By.ID, "searchpr")
            time.sleep(random.uniform(4, 7))
            actions.move_to_element(search_input).click().send_keys(self.coin_name).perform()

            submit_button = self.driver.find_element(By.ID, "search-form-button")
            time.sleep(random.uniform(2, 5))
            actions.move_to_element(submit_button).click().perform()

            product_element = self.driver.find_element(By.CLASS_NAME, "product")
            time.sleep(random.uniform(2, 6))
            actions.move_to_element(product_element).click().perform()

            logger.info(f"{self.email} | '{self.coin_name}' ==> В пошуку знайдено!", extra={'custom_color': True})

        except Exception as err:
            logger.error(f"{self.email} | '{self.coin_name}' ==> В пошуку НЕ знайдено: {err}")

    def buy(self):
        while True:
            try:
                buy_button = self.driver.find_element(By.ID, "r_buy_intovar")
                buy_button.click()
                logger.info(f"{self.browser} | {self.email} | '{self.coin_name}' ==> Додано в кошик")
                time.sleep(200)
                break
            except NoSuchElementException:
                logger.error("Кнопку 'Купити' не знайдено, оновлюю сторінку...")
                # Очікуємо 1 - 2 сек. перед наступною спробою
                time.sleep(random.uniform(1.5, 2))
                # Якщо кнопку не знайдено, перезавантажуємо сторінку
                self.driver.refresh()

            except Exception as e:
                logger.error(f"{self.browser} | {self.email} | '{self.coin_name}' ==> Не вдалося додати товар в кошик: {e}")
                time.sleep(15)
                break

    def close_driver(self):
        self.driver.quit()


class AsyncSeleniumRunner:

    def __init__(self, email, password, coin_name):
        self.link = "https://coins.bank.gov.ua/"
        self.email = email
        self.password = password
        self.coin_name = coin_name
        self.driver = None
        self.fake_useragent = None

    async def fake_user(self):
        ua = UserAgent()
        self.fake_useragent = ua.random

    async def start_driver(self):
        await self.fake_user()
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--incognito")
        chrome_options.add_argument(f'user-agent={self.fake_useragent}')
        self.driver = webdriver.Chrome(options=chrome_options)

    async def login(self):
        try:
            await self.driver.get(self.link)
            await asyncio.sleep(random.uniform(2, 4))
            actions = webdriver.ActionChains(self.driver)
            await asyncio.sleep(random.uniform(2, 5))
            login_button = await self.driver.find_element(By.CLASS_NAME, "small-menu-cabinet")

            await asyncio.sleep(random.uniform(2, 5))
            actions.move_to_element(login_button).click().perform()

            email_input = await self.driver.find_element("name", "email_address")
            await email_input.send_keys(self.email)

            password_input = await self.driver.find_element("name", "password")
            await password_input.send_keys(self.password)

            await asyncio.sleep(random.uniform(1, 3))
            login_enter = await self.driver.find_element(By.XPATH, "//button[@type='submit' and contains(text(), 'Увійти')]")
            await login_enter.click()
            logger.info(f"{self.email} ==> Авторизація пройшла успішно!", extra={'custom_color': True})
        except Exception as err:
            logger.error(f"{self.email} ==> Помилка авторизації: {err}")

    async def search(self):
        try:
            actions = webdriver.ActionChains(self.driver)
            await asyncio.sleep(random.uniform(2, 5))

            search_button = await self.driver.find_element(By.CLASS_NAME, "small-menu-search")
            await asyncio.sleep(random.uniform(2, 5))
            actions.move_to_element(search_button).click().perform()

            search_input = await self.driver.find_element(By.ID, "searchpr")
            await asyncio.sleep(random.uniform(4, 7))
            actions.move_to_element(search_input).click().send_keys(self.coin_name).perform()

            submit_button = await self.driver.find_element(By.ID, "search-form-button")
            await asyncio.sleep(random.uniform(2, 5))
            actions.move_to_element(submit_button).click().perform()

            product_element = await self.driver.find_element(By.CLASS_NAME, "product")
            await asyncio.sleep(random.uniform(2, 6))
            actions.move_to_element(product_element).click().perform()

            logger.info(f"{self.email} | '{self.coin_name}' ==> В пошуку знайдено!", extra={'custom_color': True})

        except Exception as err:
            logger.error(f"{self.email} | '{self.coin_name}' ==> В пошуку НЕ знайдено: {err}")

    async def buy(self):
        while True:
            try:
                buy_button = await self.driver.find_element(By.ID, "r_buy_intovar")
                await buy_button.click()
                logger.info(f"{self.email} | '{self.coin_name}' ==> Додано в кошик")
                await asyncio.sleep(200)
                break
            except NoSuchElementException:
                logger.error("Кнопку 'Купити' не знайдено, оновлюю сторінку...")
                await asyncio.sleep(random.uniform(1.5, 2))
                self.driver.refresh()
            except Exception as e:
                logger.error(f"{self.email} | '{self.coin_name}' ==> Не вдалося додати товар в кошик: {e}")
                await asyncio.sleep(15)
                break

    async def close_driver(self):
        await self.driver.quit()


def selenium_run(email, password, coin_name, browser='chrome'):
    runner = SeleniumRunner(email, password, coin_name, browser)
    runner.start_driver()
    runner.login()
    runner.search()
    runner.buy()
    runner.close_driver()


async def async_selenium_run(email, password, coin_name):
    runner = AsyncSeleniumRunner(email, password, coin_name=coin_name)
    await runner.start_driver()
    await runner.login()
    await runner.search()
    await runner.buy()
    await runner.close_driver()

# actions = ActionChains(self.driver)
# search_button = WebDriverWait(self.driver, 10).until(
#     EC.presence_of_element_located((By.CLASS_NAME, "small-menu-search")))
# time.sleep(random.randint(1, 3))
# actions.move_to_element(search_button).click().perform()
# search_input = self.driver.find_element(By.ID, "searchpr")
# time.sleep(random.randint(3, 6))
# search_input.send_keys(self.coin_name)
# time.sleep(random.randint(1, 3))
# submit_button = self.driver.find_element(By.ID, "search-form-button")
# submit_button.click()
# time.sleep(random.randint(1, 3))
# self.driver.find_element(By.CLASS_NAME, "product").click()
# time.sleep(random.randint(1, 3))
# logger.info(f"{self.coin_name} ==> В пошуку знайдено!", extra={'custom_color': True})

   # search_button = WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, "small-menu-search")))
