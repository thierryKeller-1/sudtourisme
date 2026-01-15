from .init_actions import *
from botasaurus.browser import Driver



def load_page(url:str) -> Driver:
    print(f"Loading page: {url}")
    driver = Driver(arguments=['--start-maximized'])
    driver.get(link=url, timeout=120)
    driver.short_random_sleep()
    return driver