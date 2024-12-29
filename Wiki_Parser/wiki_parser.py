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
        '▄' : '[france]',       #Thunderbolt Mk.1
        '◘' : '[france2]',      #Sea Hawk Mk.50
        '◗' : '[france3]',      #Fokker G.IA
        '␗' : '[china]',        #B-25J-30
        '▃' : '[usa]',          #Spitfire LF Mk IXc
        '○' : '[usa2]',          #P-36C
        '⋠' : '[usa3]',         #P-47M-1-RE
        '▂' : '[ussr]',         #P-63C-5
        "\uf059" : '[israel]',  #A-4E Early (M)
        '◡' : '[israel2]',      #Kfir C.10
        '▅' : '[japan]',        #P-51C-11-NT
        '◐' : '[italy]',       #Bf 109 F-4
        '◔' : '[italy2]',       #Yak-9P
        '▀' : '[germany]',      #Tempest Mk V
        '◄' : '[germany2]',     #Su-22M4 WTD61
        '◊' : '[germany3]'      #MiG-23BN
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
            if name in result:
                name += "_prem"
            result[name] = br
        
        return result

    def __normalize_dict(self,unit_dict : dict) -> dict:
        result = {}

        for name, br in unit_dict.items():
            for logo, utf8_logo in WikiParser.__UTF8_logos.items():
                name = name.replace(logo,utf8_logo)
            if(br == '—'):
                br = '0.0'
            name = name.replace('\\','')
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
