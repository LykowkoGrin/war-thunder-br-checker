import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
import unicodedata
import json
import os

class WikiParser:

    __UTF8_logos = {
        '▄' : '[france]',       #https://wiki.warthunder.ru/unit/thunderbolt_mk1
        '◘' : '[france2]',      #https://wiki.warthunder.ru/unit/sea_hawk_fga50_netherlands
        '◗' : '[france3]',      #https://wiki.warthunder.ru/unit/fokker_g1a
        '␗' : '[china]',        #https://wiki.warthunder.ru/unit/db_3a_china
        '▃' : '[usa]',          #https://wiki.warthunder.com/unit/spitfire_ix_usa
        '○' : '[usa2]',          #https://wiki.warthunder.ru/unit/p-36c_rb
        '⋠' : '[usa3]',         #https://wiki.warthunder.com/unit/p-47m-1-re_boxted
        '▂' : '[ussr]',         #https://wiki.warthunder.com/unit/p-63c-5_ussr
        "\uf059" : '[israel]',  #https://wiki.warthunder.com/unit/a_4e_early_iaf
        '◡' : '[israel2]',      #https://wiki.warthunder.com/unit/kfir_c10_colombia
        '▅' : '[japan]',        #https://wiki.warthunder.com/unit/f-86f-30_japan?ysclid=m5b3n4hswz675567527
        '◐' : '[italy]',       #https://wiki.warthunder.com/unit/bf-109f-4_hungary?ysclid=m5azy7g06f628044059
        '◔' : '[italy2]',       #https://wiki.warthunder.com/unit/yak-9p_hungary
        '▀' : '[germany]',      #https://wiki.warthunder.com/unit/tempest_mkv_luftwaffe
        '◄' : '[germany2]',     #https://wiki.warthunder.ru/unit/su_22m4_de_wtd61
        '◊' : '[germany3]'      #https://wiki.warthunder.ru/unit/mig_23bn
    }

    def __init__(self,path_to_edge_driver : str):
        
        service = Service(path_to_edge_driver)
        self.__driver = webdriver.Edge(service=service)

    #def __del__(self): #(very very very very very very) * 100 strannoe povedenie
    #    self.__driver.quit()
        
    def parse_in_file(self, url : str, path_to_file : str, js_wait_time = 3) -> None:
        unit_dict = {}

        self.__driver.get(url)
        time.sleep(js_wait_time)

        unit_dict = self.__handle_page_source()
        unit_dict = self.__normalize_dict(unit_dict)

        with open(path_to_file, 'w', encoding="utf-8") as file:
            json.dump(unit_dict, file, ensure_ascii=False, indent=4)

    def __handle_page_source(self) -> dict:
        html = self.__driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        result = {}

        standart_units = soup.find_all('tr', class_='wt-ulist_unit wt-ulist_unit--regular')
        premium_units = soup.find_all('tr', class_='wt-ulist_unit wt-ulist_unit--prem')
        units_element = standart_units + premium_units
        for unit in standart_units:
            name = unicodedata.normalize("NFKD",unit.find('td', class_='wt-ulist_unit-name').text)
            br = unit.find('td', class_='br').text
            result[name] = br

        for unit in premium_units:
            name = unicodedata.normalize("NFKD",unit.find('td', class_='wt-ulist_unit-name').text)
            br = unit.find('td', class_='br').text
            name += "_prem"
            result[name] = br
        
        return result

    def __normalize_dict(self,unit_dict : dict) -> dict:
        result = {}

        for name, br in unit_dict.items():
            for logo, utf8_logo in WikiParser.__UTF8_logos.items():
                if name.find(logo) != -1:
                    name = name.replace(logo,'')
                    name = utf8_logo + name
            if(br == '—'):
                br = '0.0'
            name = name.replace('\\','')
            name = name.strip()
            result[name] = float(br)
        
        
        return result
    

def main():
    print(
    """
        WAR THUNDER WIKI PARSER v1.0
        developed by Leonov Z
    """)
    base_path = os.getcwd()
    driver_path = "C:/Users/lykow/Desktop/edgedriver_win64/msedgedriver.exe"#input("Enter path to msedgedriver.exe: ")#"C:/Users/lykow/Desktop/edgedriver_win64/msedgedriver.exe"
    parser = WikiParser(driver_path)

    parser.parse_in_file(path_to_file = "eng/planes.json",
                           url="https://wiki-com.warthunder.ru/aviation?from=ru_lang&v=l",
                           js_wait_time=10)
    print(f'English data saved in {base_path}\\eng\\planes.json')

    parser.parse_in_file(path_to_file = "ru/planes.json",
                           url="https://wiki.warthunder.ru/aviation?from=en_lang&v=l",
                           js_wait_time=10)
    print(f'Russian data saved in {base_path}\\ru\\planes.json')
    
    parser.parse_in_file(path_to_file = "eng/tanks.json",
                           url="https://wiki-com.warthunder.ru/ground?from=ru_lang&v=l",
                           js_wait_time=10)
    print(f'English data saved in {base_path}\\eng\\tanks.json')

    parser.parse_in_file(path_to_file = "ru/tanks.json",
                           url="https://wiki.warthunder.ru/ground?from=en_lang&v=l",
                           js_wait_time=10)
    print(f'Russian data planes saved in {base_path}\\ru\\tanks.json')

if __name__ == '__main__':
    main()
