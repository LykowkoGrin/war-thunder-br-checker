import pytesseract
#from PIL import Image

import cv2
import numpy as np

class TextReader:

    #BLUE_HSV_MASK = [[100, 150, 50],[130, 255, 255]]
    #GREEN_HSV_MASK = [[35, 100, 100],[85, 255, 255]]

    def __init__(self,screen_resolution : str) -> None:
        self.__scan_config = r'-c tessedit_char_blacklist="[]{}|;:\$_©!?" --psm 4'
        self.__screen_resolution = screen_resolution
        
    def read_table(self,screenshot) -> list:
        left_coord = [0,0]
        right_coord = [0,0]
        if self.__screen_resolution == '1920x1080':
            left_coord[0] = 400
            left_coord[1] = 310
            right_coord[0] = 555
            right_coord[1] = 830
        #print(left_coord,right_coord)

        #hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        #mask_blue = cv2.inRange(hsv, np.array(self.BLUE_HSV_MASK[0]), np.array(self.BLUE_HSV_MASK[1]))
        #mask_green = cv2.inRange(hsv, np.array(self.GREEN_HSV_MASK[0]), np.array(self.GREEN_HSV_MASK[1]))
        #combined_mask = cv2.bitwise_or(mask_blue, mask_green)
        #cv2.imwrite('combined_mask.png', combined_mask)

        cropped_img = screenshot[left_coord[1]:right_coord[1], left_coord[0]:right_coord[0]]
        cv2.imwrite('cropped_image.png', cropped_img)
        text = pytesseract.image_to_string(cropped_img, lang="rus+eng", config=self.__scan_config)
        return text.split('\n')
    
    