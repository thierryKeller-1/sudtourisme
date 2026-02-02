import time
import unicodedata
import driver_actions as actions
from datetime import datetime, timedelta
from pathlib import Path
from botasaurus.soupify import soupify
from botasaurus.browser import Driver
from toolkits import bs4_extension as bs4_ext
from toolkits import file_manager as fm
from driver_actions import load_page
from utils import SUDTOURISME_FIELDS
from urllib.parse import urlparse, parse_qs
from driver_actions import scrap_actions as actions


class ScrapPageExtractor:
    def __init__(self, driver: Driver, metadata:dict) -> None:
        self.driver = driver
        self.selectors = metadata.get('selectors', {})
        self.data = []
        self.metadata = metadata

    def clean_text(self, text:str) -> str:
        return text.replace(',', ' - ')
    
    def get_currency(self, text:str) -> str:
        if '€' in text: return 'EUR'
        if '$' in text: return 'USD'
        return text

    def extract(self):
        name = self.clean_text(self.driver.get_text("h1[class='hn']"))
        localite = self.clean_text(self.driver.get_text("a[id='_d6fvjqzs.yz76ch5j.za4ds10u.ifutabet.dy8sg6w9']"))

        soupe = soupify(self.driver.page_html)
        cards = soupe.find("div", {'id':'_jrwmov0d.r0rmbvhs'}).find_all('li', {'class':"flex flex-col h-full justify-between p-4 rounded-md border-2 border-gray-600 hover:bg-gray-200 cursor-pointer"})
        for card in cards:
            data = {}
            data['web-scraper-order'] = ''
            data['date_price'] = self.metadata.get('week_scrap', '')
            dates = card.find('p', {'class':'font-semibold'}).text.strip().replace('Du ', '').split(' au ')         
            data['date_debut'] = dates[0]
            data['date_fin'] = dates[1]
            data['typologie'] = self.clean_text(card.find('h3', {'class':'font-semibold'}).text.strip())
            price_text = card.find('span', {'class':'text-xl text-primary font-bold'}).text.replace(',','.').split(' ')
            data['n_offre'] = ''
            data['prix_init'] = round(float(price_text[0]))
            data['prix_actuel'] = round(float(price_text[0])) 
            data['currency'] = self.get_currency(price_text[1])
            data['localite'] = localite
            data['nom'] = name
            data['date_debut-jour'] = ''
            data['Nb semaines'] = datetime.strptime(data['date_debut'], '%d/%m/%Y').isocalendar()[1]
            self.data.append(data)  

def is_date_valid(driver: Driver, metadata:dict) -> bool:
    print("validating dates...")
    soupe = soupify(driver.page_html)
    try:
        cards = soupe.find("div", {'id':'_jrwmov0d.r0rmbvhs'}).find_all('li', {'class':"flex flex-col h-full justify-between p-4 rounded-md border-2 border-gray-600 hover:bg-gray-200 cursor-pointer"})
        if cards:
            first_card = cards[0]
            date_text = first_card.find('p', {'class':'font-semibold'}).text.strip().replace('Du ', '').split(' au ')
            print(f"Expected dates: {metadata.get('date_debut')}: {date_text[0]} | {metadata.get('date_end')}: {date_text[1]}")
            meta_date_start = metadata.get('date_debut').split('-')[::-1]
            meta_date_end = metadata.get('date_end').split('-')[::-1]
            if date_text[0] == "/".join(meta_date_start) and date_text[1] == "/".join(meta_date_end):
                print("Dates are valid.")
                return True
        print("Dates are not valid.")
        return False
    except Exception as e:
        print(f"cards not found or dates invalid: {e}")
        return False

def run_scraping(metadata:dict) -> None:
    print(f"url ==> {metadata.get('current_dest')} ")
    driver = Driver(block_images=True, wait_for_complete_page_load=True)
    base_url = metadata.get("current_dest").split("?")[0]
    metadata['date_debut'] = parse_qs(urlparse(metadata.get('current_dest')).query).get('checkin')[0]
    metadata['date_end'] = parse_qs(urlparse(metadata.get('current_dest')).query).get('checkout')[0]
    driver.get(base_url)
    #check page if not 404
    try:
        if driver.select("h1[class='text-6xl font-bold text-gray-900 mb-4']").text == "404":
            print(f"Error 404 for url {base_url}")
            driver.close()
        return
    except:
        pass
    time.sleep(5)
    
    actions.accept_cookies(driver)
    actions.set_currency_to_eur(driver)
    actions.set_dates(driver, metadata.get('date_debut'), metadata.get('date_end'))

    if is_date_valid(driver, metadata):
        print("Dates correctly set.")
        extractor = ScrapPageExtractor(driver, metadata)
        extractor.extract()
        fm.save_data_to_csv(metadata.get("ouput_file"), SUDTOURISME_FIELDS, extractor.data)
    driver.close()
        
# if __name__ == "__main__":

#     run_scraping()


    
