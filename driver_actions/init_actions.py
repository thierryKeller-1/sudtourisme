from botasaurus.soupify import soupify
import toolkits.bs4_extension as bs4_ext
import time

def accept_cookies(driver):
    print("Accepting cookies...")
    try:
        driver.click_element_containing_text("Accepter")
        driver.short_random_sleep()
    except Exception:
        pass

def filter_accommodations(driver, selectors):
    print("Filtering accommodations...")
    try:
        driver.scroll_into_view(bs4_ext.create_selector(selectors.get("accomodation_filter"))) 
        time.sleep(5)
        driver.click(bs4_ext.create_selector(selectors.get("hotel_filter")))
        time.sleep(5)
        # driver.click(bs4_ext.create_selector(selectors.get("gite_filter")))
        # time.sleep(5)
    except Exception:
        pass

def get_page_number(driver, selectors) -> int:
    print("Getting page number...")
    try:
        soupe_element = soupify(driver.select(bs4_ext.create_selector(selectors.get('pagination'))))
        page_items = bs4_ext.get_all_element_by_locator(soupe_element, selectors.get("pages"))
        # print(page_items[-1])
        page_number = bs4_ext.extract_element_by_locator(page_items[-1], selectors.get("page"))
        if page_number:
            return int(page_number)
    except Exception:
        print("Page number not found.")
        return