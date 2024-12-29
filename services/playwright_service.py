import asyncio
import random
from idlelib.grep import walk_error

from playwright.async_api import async_playwright, Playwright
from playwright.sync_api import sync_playwright, ProxySettings

from services.proxy_service import get_random_proxy, load_proxies
from utils.py_logger import get_logger

logger = get_logger(__name__)

LINK = "https://coins.bank.gov.ua/login.php"


class PlaywrightAsyncRunner:

    def __init__(self, email, password, coin_name, link, headless=False):
        """
        Ініціалізує об'єкт з необхідними параметрами.
        """
        self.email = email
        self.password = password
        self.coin_name = coin_name
        self.link = link
        self.headless = headless
        self.browser = None
        self.page =None

    async def _setup_browser(self, playwright) -> None:
        """
        Налаштовує браузер і сторінку.
        """
        firefox = playwright.firefox
        self.browser =await firefox.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        await self.page.goto(self.link)

    async def _close_browser(self):
        """
        Закриття браузера
        """
        if self.browser:
            await self.browser.close()

    async def _log_user_agent(self):
        """
        Логування User-Agent браузера.
        """
        user_agent = await self.page.evaluate("navigator.userAgent")
        logger.info(f"{self.email} | User-Agent: {user_agent}", extra={'custom_color': True})

    async def _accept_cookies(self):
        """
        Приймає cookies, якщо з'являється відповідне вікно.
        """
        try:
            await self.page.locator('a.cc-btn.cc-allow').click()
            logger.info(f"{self.email} | Clicked 'Дозволити' on the cookie consent.", extra={'custom_color': True})
        except Exception as e:
            logger.warning(f"{self.email} | Failed to click 'Дозволити': {e}")

    async def _login(self):
        """
        Авторизація на сайті.
        """
        try:
            await asyncio.sleep(random.randint(1, 3))
            await self.page.locator("input[name='email_address']").fill(self.email)
            await self.page.locator("input[name='password']").fill(self.password)

            await asyncio.sleep(random.randint(2, 3))
            login_button = await self.page.wait_for_selector('button[class="btn btn-default"]', state='visible')
            await login_button.scroll_into_view_if_needed()  # Прокрутити його в поле зору
            await login_button.focus()  # Фокус на елемент
            await login_button.click()  # Натискання на елемент
            logger.info(f"{self.email} ==> Авторизація пройшла успішно!", extra={'custom_color': True})
        except Exception as e:
            logger.error(f"{self.email} | Login failed: {e}")
            raise

    async def _search(self):
        """
        Пошук продукту на сайті.
        """
        try:
            await asyncio.sleep(random.randint(1, 3))
            await self.page.locator(".small-menu-search").click()
            await self.page.locator("#searchpr").fill(self.coin_name)
            await self.page.locator("#search-form-button").click()
            await self.page.wait_for_selector("div.product", state="visible")

            await asyncio.sleep(random.randint(1, 3))
            await self.page.locator("div.product").click()
            logger.info(f"{self.email} | '{self.coin_name}' в пошуку знайдено!", extra={'custom_color': True})
        except Exception as e:
            logger.error(f"{self.email} | Search failed: {e}")
            raise

    async def _buy(self):
        """
        Купівля знайденого продукту.
        """
        max_attempts = 5  # Максимальна кількість спроб
        attempt = 0

        while attempt < max_attempts:
            try:
                await asyncio.sleep(random.randint(1, 3))
                buy_button_count = await self.page.locator("div#r_buy_intovar").count()

                if buy_button_count > 0:
                    buy_button = self.page.locator("div#r_buy_intovar")
                    await buy_button.focus()
                    await buy_button.click()
                    logger.info(f"{self.email} | '{self.coin_name}' успішно додано в кошик.",
                                extra={'custom_color': True})
                    return
                else:
                    logger.warning(
                        f"{self.email} | Кнопка 'Купити' не знайдена. Спроба #{attempt + 1}. Перезавантаження сторінки...")
                    await asyncio.sleep(random.randint(1, 2))
                    await self.page.reload()
                    attempt += 1
            except Exception as e:
                logger.error(f"{self.email} | Помилка під час покупки: {e}")
                raise

        logger.error(f"{self.email} | Не вдалося знайти кнопку 'Купити' після {max_attempts} спроб.")
        raise RuntimeError("Купівля не вдалася після декількох спроб.")

    async def buy_coins(self, playwright: Playwright):
        """
        Основний метод, який запускає всі етапи процесу.
        """
        try:
            await self._setup_browser(playwright)
            await self._log_user_agent()
            await self._accept_cookies()
            await self._login()
            await self._search()
            await self._buy()
        except Exception as e:
            logger.error(f"{self.email} | Error during operation: {e}")
        finally:
            await self._close_browser()


async def playwright_async_run(email, password, coin_name, link=LINK):
    """
    Головна функція для запуску операцій.
    """
    runner = PlaywrightAsyncRunner(email, password, coin_name, link)
    async with async_playwright() as playwright:
        await runner.buy_coins(playwright)
