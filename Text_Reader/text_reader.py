import pytesseract
#from PIL import Image

import cv2
import numpy as np
import os

class TextReader:
    __LOGO_SIMILARITY_COEFF = 0.7
    __PREMIUM_COLOR_MIN_AREA = 40

    def __init__(self,screen_resolution : str) -> None:
        self.__scan_config = r'-c tessedit_char_blacklist="[]{}|;:\$_©!?" --psm 7'
        self.__screen_resolution = screen_resolution
        self.__nation_logos = {}

        self.__load_nation_logos()
        #print(self.__nation_logos)
        
    def read_table(self,screenshot) -> list:
        vehicle_name_start_coord = [0,0]
        vehicle_name_box = [0,0]

        vehicle_icon_start_coord = [0,0]
        vehicle_icon_box = [0,0]
        if self.__screen_resolution == '1920x1080':
            vehicle_name_start_coord = [390,314]
            vehicle_name_box = [170,27]

            vehicle_icon_start_coord = [560,314]
            vehicle_icon_box = [40,27]

        units_name = []

        for i in range(0,16):
            left_coord =  [vehicle_name_start_coord[0], vehicle_name_start_coord[1] + i * vehicle_name_box[1]]
            right_coord = [vehicle_name_start_coord[0] + vehicle_name_box[0], vehicle_name_start_coord[1] + (i + 1) * vehicle_name_box[1]]
            
            left_icon_coord =  [vehicle_icon_start_coord[0], vehicle_icon_start_coord[1] + i * vehicle_icon_box[1]]
            right_icon_coord = [vehicle_icon_start_coord[0] + vehicle_icon_box[0], vehicle_icon_start_coord[1] + (i + 1) * vehicle_icon_box[1]]
            
            cropped_img = screenshot[left_coord[1] : right_coord[1], left_coord[0] : right_coord[0]]
            cropped_icon = screenshot[left_icon_coord[1] : right_icon_coord[1], left_icon_coord[0] : right_icon_coord[0]]
            logo_name, _ = self.__find_nation_logo(cropped_img)

            is_prem = self.__check_for_prem(cropped_icon)
            #cv2.imwrite(f"{i}.png",cropped_icon)


            #if logo_name != '':
            #    cv2.rectangle(cropped_img, (logo_box[0], logo_box[1]), (logo_box[2], logo_box[3]), (0, 0, 0), thickness=-1)
                #cv2.imwrite(f"{i}.png",cropped_img)
            
            name = pytesseract.image_to_string(cropped_img, lang="rus+eng", config=self.__scan_config)
            name = name.replace('\n','')
            name = logo_name + name
            name += "_prem" if is_prem else ""
            units_name.append(name)
        
        return units_name
    
    def __find_nation_logo(self,img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img_bin = cv2.threshold(img_gray, 70, 255, cv2.THRESH_BINARY)
        
        found_logos = []

        for logo_name, logo_img in self.__nation_logos.items():
            logo_info = self.__find_bin_logo(img_bin,logo_img)
            logo_info['name'] = logo_name
            found_logos.append(logo_info)

        #print(found_logos)
        best_logo = max(found_logos,key= lambda item : item['match_value'])
        if(best_logo['match_value'] >= self.__LOGO_SIMILARITY_COEFF):
            template_height, template_width = self.__nation_logos[best_logo['name']].shape[:2]
            x = best_logo['location'][0]
            y = best_logo['location'][1]
            w = template_width * best_logo['scale']
            h = template_height * best_logo['scale']
            return best_logo['name'],(x,y,int(x + w),int(y + h))
        
        return '',(0,0,0,0)
    
    def __load_nation_logos(self):

        for filename in os.listdir('Text_Reader/logos'):
            if filename.endswith(".png"):
                file_path = os.path.join('Text_Reader/logos', filename)

                image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                if image is None:
                    print(f"Не удалось загрузить изображение: {filename}")
                    continue

                self.__nation_logos[os.path.splitext(filename)[0]] = image
    

    @staticmethod
    def __find_bin_logo(bin_img,bin_logo,scale_range=(0.3, 0.4),scale_step=0.01) -> dict:
        best_match = {
            'match_value' : -1,
            'location' : None,
            'scale' : None
        }

        for scale in np.arange(scale_range[0], scale_range[1] + scale_step, scale_step):
            scaled_logo = cv2.resize(bin_logo, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)

            if scaled_logo.shape[0] > bin_img.shape[0] or scaled_logo.shape[1] > bin_img.shape[1]:
                continue

            result = cv2.matchTemplate(bin_img, scaled_logo, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val > best_match['match_value']:
                best_match['match_value'] = max_val
                best_match['location'] = max_loc
                best_match['scale'] = scale

        return best_match

    def __check_for_prem(self,vehicle_icon) -> bool:

        hsv_image = cv2.cvtColor(vehicle_icon, cv2.COLOR_BGR2HSV)

        lower_orange_red = np.array([0, 50, 50])      
        upper_orange_red = np.array([20, 255, 255])   

        mask = cv2.inRange(hsv_image, lower_orange_red, upper_orange_red)

        white_points = cv2.countNonZero(mask)

        return white_points > self.__PREMIUM_COLOR_MIN_AREA
