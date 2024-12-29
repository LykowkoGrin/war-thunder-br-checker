from Text_Reader.text_reader import TextReader
from Unit_Grabber.unit_grabber import UnitGrabber
import json
#from PIL import Image
import cv2


def main():
    print(
    """
        WAR BOMBING v1.0
        developed by Leonov Z
    """)
    units = {}
    with open("Wiki_Parser/ru/tanks.json", 'r', encoding='utf-8') as file:
        units = json.load(file)
    
    grabber = UnitGrabber(units)
    reader = TextReader('1920x1080')

    image = cv2.imread('Test_Data/screenshot.png', cv2.IMREAD_UNCHANGED)#Image.open("Test_Data/cut4.png")
    units_list = reader.read_table(image)
    
    for unit_name in units_list:
        if len(unit_name) < 2:
            continue
        br = grabber.get_unit_br(unit_name,7.7)
        if br == None:
            continue
        print(unit_name,br)
        


    #img = Image.open('Test_Data/cut6.png') #без эмблем
    #print(reader.read_table(img))
    

if __name__ == "__main__":
    main()