import random
import time
from dotenv import dotenv_values
from playwright.sync_api import sync_playwright, ProxySettings

from services.proxy_service import get_random_proxy, load_proxies
from utils.py_logger import get_logger

logger = get_logger(__name__)
config = dotenv_values(".env")
EMAIL_NBU = config.get("EMAIL_NBU")
PASSWORD_NBU = config.get("PASSWORD_NBU")
EMAIL_NBU_MASHA = config.get("EMAIL_NBU_MASHA")
PASSWORD_NBU_MASHA = config.get("PASSWORD_NBU_MASHA")

link = "https://coins.bank.gov.ua/login.php"


class PlaywrightRunner:
    def __init__(self, email, password, coin_name):
        self.proxy_settings = self.get_proxy_settings()
        self.email = email
        self.password = password
        self.coin_name = coin_name

    @staticmethod
    def get_proxy_settings():
        proxy = get_random_proxy()
        proxy_setting = ProxySettings(
            server=proxy.get('PROXY_SERVER'),
            username=proxy.get('PROXY_USERNAME'),
            password=proxy.get('PROXY_PASSWORD')
        )
        return proxy_setting

    def refresh_proxy(self):
        # Завантаження нових проксі з API та збереження їх у файл
        load_proxies()
        # Свіжий проксі
        self.proxy_settings = self.get_proxy_settings()

    def handle_proxy_error(self, err):
        if "NS_ERROR_PROXY_CONNECTION_REFUSED" in str(err):
            logger.error("ERROR: NOT connect to the proxy.")
            self.refresh_proxy()
            logger.info("New Proxy update.")
            return True
        return False

    def buy_coins(self) -> str | None:
        try:
            with sync_playwright() as playwright:
                firefox = playwright.firefox
                browser = firefox.launch(headless=False)
                page = browser.new_page()
                page.goto(link)
                # screenshot = page.screenshot()

                # Click on the login button
                page.fill("input[name='email_address']", self.email)
                page.fill("input[name='password']", self.password)
                time.sleep(random.randint(1, 3))
                page.locator('button[class="btn btn-default"]').click()
                # page.get_by_text("Увійти").click()
                time.sleep(random.randint(1, 3))
                # Search for the product
                page.wait_for_selector(".small-menu-search").click()  # кнопка пошукового вікна
                page.wait_for_selector("#searchpr").fill(self.coin_name)  # вікно для введення тексту
                page.wait_for_selector("#search-form-button").click()  # кнопка запуску пошуку
                page.wait_for_selector("div.product").click()  # Кнопка запиту продукту
                logger.info(f"{self.coin_name} в пошуку знайдено!")
                time.sleep(random.randint(1, 3))
                # Click on the product and buy it
                try:
                    buy_product = page.wait_for_selector("div#r_buy_intovar", state='visible')  # Кнопка "Купити"
                    buy_product.click()
                    logger.info(f"'{self.coin_name}' успішно додано в кошик.", extra={'custom_color': True})
                    time.sleep(25)
                except Exception as err:
                    logger.error(f"Не вдалося додати товар в кошик: {err}")
                finally:
                    browser.close()

                return
        except Exception as e:
            if self.handle_proxy_error(e):
                return self.buy_coins()
            logger.error(f"PlaywrightRunner Error: {e}")
            return None

        # login_button = page.wait_for_selector("button.btn.btn-default", state='visible')
        # login_button.click()

        # Заповнюємо дані для входу
        # page.fill("input[name='email_address']", self.email)
        # page.fill("input[name='password']", self.password)
        #
        # # Натискаємо на кнопку "Увійти"
        # try:
        #     submit_button = page.get_by_text("Увійти")
        #     submit_button.click()
        #     logger.info(f"{self.email} - Успішно ввійшов в аккаунт!", extra={'custom_color': True})
        # except TimeoutError:
        #     logger.error(f"{self.email} - Не вдалося знайти або натиснути кнопку 'Увійти'!")


def playwright_run(coin_name):
    runner = PlaywrightRunner(EMAIL_NBU, PASSWORD_NBU, coin_name)
    runner.buy_coins()
