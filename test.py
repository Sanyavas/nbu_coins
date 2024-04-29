import random

from services.playwright_service import playwright_run
from services.selenium_service import selenium_run, SeleniumRunner

# COIN_NAME = "Єдність рятує світ"
# COIN_NAME = "Східний календар"
# COIN_NAME = "Боспорське царство"
# COIN_NAME = "Сміливість бути. UA"
COIN_NAME = "І.Франка"


if __name__ == '__main__':
    print(random.uniform(1.5, 6))

