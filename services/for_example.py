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

                # Click "Allow" for cookies
                try:
                    page.click('a.cc-btn.cc-allow')  # Click using class selector
                    logger.info("Clicked 'Allow' on the cookie consent.")
                except Exception as e:
                    logger.error(f"Failed to click 'Allow' on the cookie consent: {e}")

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


def playwright_run_test(email_nbu, password_nbu, coin_name):
    runner = PlaywrightRunner(email_nbu, password_nbu, coin_name)
    runner.buy_coins()


"""Exampl with proxy"""
# class PlaywrightRunner:
#     def __init__(self, email, password, coin_name):
#         self.proxy_settings = self.get_proxy_settings()
#         self.email = email
#         self.password = password
#         self.coin_name = coin_name
#
#     @staticmethod
#     def get_proxy_settings():
#         proxy = get_random_proxy()
#         proxy_setting = ProxySettings(
#             server=proxy.get('PROXY_SERVER'),
#             username=proxy.get('PROXY_USERNAME'),
#             password=proxy.get('PROXY_PASSWORD')
#         )
#         return proxy_setting
#
#     def refresh_proxy(self):
#         # Завантаження нових проксі з API та збереження їх у файл
#         load_proxies()
#         # Свіжий проксі
#         self.proxy_settings = self.get_proxy_settings()
#
#     def handle_proxy_error(self, err):
#         if "NS_ERROR_PROXY_CONNECTION_REFUSED" in str(err):
#             logger.error("ERROR: NOT connect to the proxy.")
#             self.refresh_proxy()
#             logger.info("New Proxy update.")
#             return True
#         return False
#
#     def buy_coins(self):
#         try:
#             with sync_playwright() as playwright:
#                 firefox = playwright.firefox
#                 browser = firefox.launch(headless=False)  # now without proxy
#                 page = browser.new_page()
#                 page.goto(link)
#
#                 # Get User-Agent
#                 user_agent = page.evaluate("navigator.userAgent")
#                 logger.info(f"User-Agent: {user_agent}")
#
#                 # Click "Дозволити" for cookies
#                 try:
#                     page.click('a.cc-btn.cc-allow')  # Click using class selector
#                     logger.info("Clicked 'Дозволити' on the cookie consent.")
#                 except Exception as e:
#                     logger.error(f"Failed to click 'Дозволити' on the cookie consent: {e}")
#
#                 # fill and click on the login button
#                 time.sleep(random.randint(3, 5))
#                 page.fill("input[name='email_address']", self.email)
#                 page.fill("input[name='password']", self.password)
#                 time.sleep(random.randint(2, 3))
#                 login_button = page.wait_for_selector('button[class="btn btn-default"]', state='visible')
#                 login_button.focus()  # Фокус на елемент
#                 login_button.click()  # Клік на елемент
#                 # buy_product.tap()  # Натискання (для мобільних)
#                 # buy_product.dispatch_event("click")  # Виклик події кліку
#                 logger.info(f"{self.email} ==> Авторизація пройшла успішно!", extra={'custom_color': True})
#
#                 # page.get_by_text("Увійти").click()
#
#                 # Search for the product
#                 time.sleep(random.randint(1, 3))
#                 page.wait_for_selector(".small-menu-search").click()  # кнопка пошукового вікна
#                 page.wait_for_selector("#searchpr").fill(self.coin_name)  # вікно для введення тексту
#                 page.wait_for_selector("#search-form-button").click()  # кнопка запуску пошуку
#                 time.sleep(random.randint(1, 3))
#                 page.wait_for_selector("div.product").click()  # Кнопка запиту продукту
#                 logger.info(f"{self.email} | '{self.coin_name}' в пошуку знайдено!")
#
#                 # Click on the product and buy
#                 try:
#                     time.sleep(random.randint(1, 3))
#                     buy_product = page.wait_for_selector("div#r_buy_intovar", state='visible')  # Кнопка "Купити"
#                     buy_product.focus()
#                     buy_product.click()
#                     logger.info(f"{self.email} | '{self.coin_name}' успішно додано в кошик.",
#                                 extra={'custom_color': True})
#                     time.sleep(25)
#                 except Exception as err:
#                     logger.error(f"{self.email} | '{self.coin_name}' Не вдалося додати товар в кошик: {err}")
#                 finally:
#                     browser.close()
#                 return
#         except Exception as e:
#             if self.handle_proxy_error(e):
#                 return self.buy_coins()
#             logger.error(f"{self.email} | PlaywrightRunner Error: {e}")
#             return None
#
#         # login_button = page.wait_for_selector("button.btn.btn-default", state='visible')
#         # login_button.click()

