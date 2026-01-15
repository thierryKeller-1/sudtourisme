import time
import os
import unicodedata
import driver_actions as actions
from datetime import datetime, timedelta
from pathlib import Path
from botasaurus.soupify import soupify
from botasaurus.browser import Driver
from toolkits import bs4_extension as bs4_ext
from toolkits.file_manager import get_json_file_content, save_json_data
from driver_actions import load_page
from dotenv import load_dotenv

load_dotenv()

class InitialiserPageExtractor:
    def __init__(self, driver: Driver, selectors:dict) -> None:
        self.driver = driver
        self.selectors = selectors
        self.data = []

    def extract(self):
        container = soupify(self.driver.select(bs4_ext.create_selector(self.selectors.get("container"))))
        # print(container)
        datas = bs4_ext.get_all_element_by_locator(container, self.selectors.get("datas"))
        # print(len(datas))
        for data in datas:
            item = {}
            for key in self.selectors.get("data").keys():
                field_selector = self.selectors.get("data").get(key)
                item[key] = bs4_ext.extract_element_by_locator(data, field_selector)
            self.data.append(item)

    def format_text(self, text: str) -> str:
        normalized_text = "".join(c for c in unicodedata.normalize('NFD', text) if not unicodedata.combining(c))
        normalized_text = normalized_text.replace('\u2019', "'").replace(' & ', ' and ').replace(' - ', ' ')
        return normalized_text

    def save_data(self, file_path: str) -> None:
        new_data = []
        for data in self.data:
            data["name"] = self.format_text(data["name"])
            new_data.append(data)
        save_json_data(file_path, new_data)


class InitialiserSetup:
    def __init__(self, metadata:dict) -> None:
        self.dest_name = metadata.get("dest_name")
        self.weekscrap = metadata.get("week_scrap")
        self.start_date = datetime.strptime(metadata.get('start_date'), "%d/%m/%Y")
        self.end_date = datetime.strptime(metadata.get('end_date'), "%d/%m/%Y")
        self.freq = int(metadata.get('frequency'))
        self.stations = []
        self.nomralized_urls = []
        self.urls = []
        
    def load_destination(self) -> None:
        self.stations = get_json_file_content(f"{os.environ.get("DESTS_FOLDER_PATH")}/init/{self.weekscrap.replace('/', '_')}/{self.dest_name}.json")

    def normalize_url(self) -> list:
        base_url = "https://www.book-sudtourisme.com/reserver-mon-hebergement/"
        for station in self.stations:
            normalized_url = base_url + station['name'].lower().replace(' ', '-').replace("'", '-') 
            self.nomralized_urls.append({"station": station['name'], "url": normalized_url, "detail_url": station['url']})
    
    def generate_urls(self) -> None:
        date_space = int((self.end_date - self.start_date).days) + 1
        checkin = self.start_date
        checkout = checkin + timedelta(days=self.freq)  
        if self.freq in [1, 3, 7]:
            for _ in range(date_space):
                for url in self.nomralized_urls:
                    url = url.get('url') + f"?checkin={checkin.strftime('%Y-%m-%d')}&checkout={checkout.strftime('%Y-%m-%d')}"
                    self.urls.append(url)
                checkin += timedelta(days=1)
                checkout = checkin + timedelta(days=self.freq)
        return self.urls


def run_initialization(metadata:str) -> None:
    selectors = get_json_file_content(f"{os.environ.get("PROJECT_FOLDER_PATH")}/init_selector.json")
    driver = load_page(selectors["base_url"])
    actions.accept_cookies(driver)
    actions.filter_accommodations(driver, selectors)
    page_number = actions.get_page_number(driver, selectors)
    if page_number:
        for i in range(1, page_number+1):
            print("extraction process ")
            init_page = InitialiserPageExtractor(driver, selectors.get('data_extraction'))
            init_page.extract()
            init_page.save_data(f"{os.environ.get('DESTS_FOLDER_PATH')}/init/{metadata.get('week_scrap').replace('/', '_')}/{metadata.get('dest_name')}.json")
            if i < page_number:
                next_page_button = bs4_ext.create_selector(selectors.get("next_page_button"))
                driver.scroll_into_view(next_page_button)
                driver.click(next_page_button)
            time.sleep(5)
            

def setup_scraping(metadata:dict) -> None:
    setup = InitialiserSetup(metadata)
    setup.load_destination()
    setup.normalize_url()
    urls = setup.generate_urls()
    print(urls)
    save_json_data(f"{os.environ.get('DESTS_FOLDER_PATH')}/scraps/{setup.weekscrap.replace('/', '_')}/{setup.dest_name}_{setup.freq}j.json", urls)


# if __name__ == "__main__":
#     run_initialization()
#     setup_scraping()