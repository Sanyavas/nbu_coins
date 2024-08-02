import random

from services.playwright_service import playwright_run
from services.selenium_service import selenium_run, SeleniumRunner

# COIN_NAME = "Єдність рятує світ"
# COIN_NAME = "Східний календар"
# COIN_NAME = "Боспорське царство"
# COIN_NAME = "Сміливість бути. UA"
COIN_NAME = "І.Франка"


if __name__ == '__main__':
    from datetime import datetime
    import pytz

    # Конвертація з UTC в локальний час
    utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
    local_timezone = pytz.timezone('Europe/Kiev')
    local_time = utc_time.astimezone(local_timezone)
    print("Local time:", local_time)

    # Конвертація з локального часу в UTC
    utc_time = local_time.astimezone(pytz.utc)
    print("UTC time:", utc_time)

