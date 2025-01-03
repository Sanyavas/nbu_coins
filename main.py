import asyncio
from datetime import datetime, timedelta
import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from dotenv import dotenv_values


from services.playwright_service import playwright_async_run
from services.proxy_service import get_random_proxy
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
COIN_NAME = "Цифрова держава"
# COIN_NAME = "Чорнобиль. Відродження. Лелека чорний"
COIN_NAME1 = "Єдність рятує світ"


COIN_NAME = "Східний календар"

# COIN_NAME = ["Східний календар", "Єдність рятує світ", "І.Франка"]


async def main_cron_run(task_planner=False):
    try:
        if task_planner:
            logger.info("BUY COINS Started with Job Scheduler", extra={'custom_color': True})
            start_time = datetime.now().replace(hour=23, minute=41, second=0, microsecond=0)
            if datetime.now() > start_time:
                start_time += timedelta(days=1)

            trigger = DateTrigger(run_date=start_time)

            # coin_name = random.choice(coin_name)
            # Додаємо завдання до scheduler з використанням trigger
            scheduler.add_job(func=playwright_async_run, args=(EMAIL_NBU, PASSWORD_NBU, COIN_NAME), trigger=trigger)
            scheduler.add_job(func=playwright_async_run, args=(EMAIL_NBU_DIMA, PASSWORD_NBU_DIMA, COIN_NAME), trigger=trigger)

            scheduler.start()
            await asyncio.sleep(3600)
            logger.info("BUY COINS Stopped with Job Scheduler", extra={'custom_color': True})
            scheduler.shutdown(wait=False)

        #запуск без планувальника
        logger.info(f"{EMAIL_NBU} | BUY COINS Started", extra={'custom_color': True})
        await playwright_async_run(email=EMAIL_NBU, password=PASSWORD_NBU, coin_name=COIN_NAME)
        logger.info(f"{EMAIL_NBU} | BUY COINS Stopped", extra={'custom_color': True})

    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == '__main__':
    asyncio.run(main_cron_run())

    # selenium_run(EMAIL_NBU, PASSWORD_NBU, COIN_NAME1)
    # playwright_run(EMAIL_NBU, PASSWORD_NBU, COIN_NAME1)

    # playwright_run(EMAIL_NBU, PASSWORD_NBU, COIN_NAME)

    # playwright_run_test(EMAIL_NBU_DIMA, PASSWORD_NBU_DIMA, COIN_NAME)
    # get_random_proxy()

