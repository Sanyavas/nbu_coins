import random
import time
from dotenv import dotenv_values
from playwright.sync_api import sync_playwright, ProxySettings

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
        self.email = email
        self.password = password
        self.coin_name = coin_name

    def buy_coins(self):
        try:
            with sync_playwright() as playwright:
                firefox = playwright.firefox
                browser = firefox.launch(headless=False)  # now without proxy
                page = browser.new_page()
                page.goto(link)

                # Get User-Agent
                user_agent = page.evaluate("navigator.userAgent")
                logger.info(f"User-Agent: {user_agent}")

                # Fill in the login form
                page.fill("input[name='email_address']", self.email)
                page.fill("input[name='password']", self.password)
                time.sleep(random.randint(1, 3))
                page.locator('button[class="btn btn-default"]').click()

                # Log successful login
                logger.info(f"{self.email} - Успішно ввійшов в аккаунт!", extra={'custom_color': True})

                # Search for the product
                page.wait_for_selector(".small-menu-search").click()  # кнопка пошукового вікна
                page.wait_for_selector("#searchpr").fill(self.coin_name)  # вікно для введення тексту
                page.wait_for_selector("#search-form-button").click()  # кнопка запуску пошуку
                page.wait_for_selector("div.product").click()  # Кнопка запиту продукту
                logger.info(f"{self.coin_name} в пошуку знайдено!")
                time.sleep(random.randint(1, 3))

                # Try to buy the product
                try:
                    buy_product = page.wait_for_selector("div#r_buy_intovar", state='visible')  # Кнопка "Купити"
                    buy_product.click()
                    logger.info(f"'{self.coin_name}' успішно додано в кошик.", extra={'custom_color': True})
                    time.sleep(25)
                except Exception as err:
                    logger.error(f"Не вдалося додати товар в кошик: {err}")
                finally:
                    browser.close()

        except Exception as e:
            logger.error(f"PlaywrightRunner Error: {e}")


def playwright_run_test(coin_name):
    runner = PlaywrightRunner(EMAIL_NBU, PASSWORD_NBU, coin_name)
    runner.buy_coins()

if __name__ == '__main__':

    # Приклад запуску
    playwright_run_test("Східний календар")

