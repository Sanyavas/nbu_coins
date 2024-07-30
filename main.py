import asyncio
from datetime import datetime, timedelta
import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from dotenv import dotenv_values

from services.for_example import playwright_run_test
from services.playwright_service import playwright_run
from services.selenium_service import selenium_run, async_selenium_run
from utils.py_logger import get_logger

logger = get_logger(__name__)
scheduler = AsyncIOScheduler()
config = dotenv_values(".env")

EMAIL_NBU = config.get("EMAIL_NBU")
PASSWORD_NBU = config.get("PASSWORD_NBU")
EMAIL_NBU_MASHA = config.get("EMAIL_NBU_MASHA")
PASSWORD_NBU_MASHA = config.get("PASSWORD_NBU_MASHA")
EMAIL_NBU_DIMA = config.get("EMAIL_NBU_DIMA")
PASSWORD_NBU_DIMA = config.get("PASSWORD_NBU_DIMA")

# COIN_NAME = "Сміливість бути. UA"
# COIN_NAME = "Пам`ятна банкнота номіналом 20 грн. до 160-річчя від дня народження І.Франка"
COIN_NAME = "Східний календар"
# COIN_NAME = "Чорнобиль. Відродження. Лелека чорний"
COIN_NAME1 = "160-річчя від дня народження І.Франка"


# COIN_NAME = "Нептун"

# COIN_NAME = ["Східний календар", "Єдність рятує світ", "І.Франка"]


async def main_cron_run():
    try:
        logger.info("Scheduler started", extra={'custom_color': True})
        start_time = datetime.now().replace(hour=23, minute=41, second=0, microsecond=0)
        if datetime.now() > start_time:
            start_time += timedelta(days=1)

        trigger = DateTrigger(run_date=start_time)

        # coin_name = random.choice(coin_name)
        # Додаємо завдання до scheduler з використанням trigger
        scheduler.add_job(func=playwright_run, args=(EMAIL_NBU, PASSWORD_NBU, COIN_NAME), trigger=trigger)
        scheduler.add_job(func=playwright_run, args=(EMAIL_NBU_DIMA, PASSWORD_NBU_DIMA, COIN_NAME), trigger=trigger)

        # scheduler.add_job(func=selenium_run, args=(EMAIL_NBU, PASSWORD_NBU, COIN_NAME1), trigger=trigger)
        # scheduler.add_job(func=selenium_run, args=(EMAIL_NBU_MASHA, PASSWORD_NBU_MASHA, COIN_NAME), trigger=trigger)
        # scheduler.add_job(func=selenium_run, args=(EMAIL_NBU_DIMA, PASSWORD_NBU_DIMA, COIN_NAME, "chrome"), trigger=trigger)

        # scheduler.add_job(func=selenium_run, args=(EMAIL_NBU, PASSWORD_NBU, COIN_NAME, "firefox"), trigger=trigger)
        # scheduler.add_job(func=selenium_run, args=(EMAIL_NBU_MASHA, PASSWORD_NBU_MASHA, COIN_NAME1, "firefox"), trigger=trigger)
        # scheduler.add_job(func=selenium_run, args=(EMAIL_NBU_DIMA, PASSWORD_NBU_DIMA, COIN_NAME1, "firefox"), trigger=trigger)
        scheduler.start()
        await asyncio.sleep(3600)
        logger.info("Scheduler stopped", extra={'custom_color': True})
        scheduler.shutdown(wait=False)
    except Exception as e:
        logger.error(f"Error: {e}")


# if __name__ == '__main__':
#     # asyncio.run(main_cron_run())
#
#     # selenium_run(EMAIL_NBU, PASSWORD_NBU, COIN_NAME1)
#     # playwright_run(EMAIL_NBU, PASSWORD_NBU, COIN_NAME1)
#     playwright_run(EMAIL_NBU_DIMA, PASSWORD_NBU_DIMA, COIN_NAME1)

if __name__ == '__main__':

    # Приклад запуску
    playwright_run_test("Східний календар")
