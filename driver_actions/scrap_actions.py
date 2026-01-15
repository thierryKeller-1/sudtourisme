import time


def accept_cookies(driver) -> None:
    try:
        driver.click_element_containing_text("Accepter")
        time.sleep(1)
    except:
        pass

def set_currency_to_eur(driver) -> None:
    try:
        driver.click_element_containing_text("XPF")
        time.sleep(1)
        driver.click_element_containing_text("EUR")
        time.sleep(1)
    except:
        pass

def set_dates(driver, start_date:str, end_date:str) -> None:
    try:
        driver.scroll_into_view("input[id='datepicker-v-0-1-1-0-start']")
        time.sleep(1)
        driver.run_js(f"""
            let date_start = document.getElementById('datepicker-v-0-1-1-0-start');
            date_start.value = "{start_date}";

            date_start.scrollIntoView();

            date_start.dispatchEvent(new Event('input', {{ bubbles : true }} ));
            date_start.dispatchEvent(new Event('change', {{ bubbles : true }} ));

            let date_end = document.getElementById('datepicker-v-0-1-1-0-end');
            date_end.value = "{end_date}";

            date_end.dispatchEvent(new Event('input', {{ bubbles : true }} ));
            date_end.dispatchEvent(new Event('change', {{ bubbles : true }} ));
            """)
        time.sleep(2)
        
        driver.click_element_containing_text("Rechercher")

        time.sleep(5)
    except Exception as e:
        print(f"Error setting dates: {e}")
