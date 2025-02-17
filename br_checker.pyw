from Text_Reader.text_reader import TextReader
from Unit_Grabber.unit_grabber import UnitGrabber

import json
import threading
from tkinter import *
from PIL import Image, ImageTk, ImageGrab
import keyboard
import time
import numpy as np


class BrChecker:

    def change_units_dict(self, load_planes: bool, load_tanks: bool):
        self.__units = {}
        if load_planes:
            with open(f"{self.__unit_names_path}{self.__language}/planes.json", 'r', encoding='utf-8') as file:
                self.__units.update(json.load(file))
        if load_tanks:
            with open(f"{self.__unit_names_path}{self.__language}/tanks.json", 'r', encoding='utf-8') as file:
                self.__units.update(json.load(file))

    def save_settings(self):
        settings_dict = {
            "language": self.__language,
            'screenshot_key': self.__screenshot_key,
            "resolution": self.__resolution,
            "logos_path": self.__logos_path,
            "unit_names_path": self.__unit_names_path
        }
        with open("settings.json", 'w', encoding="utf-8") as file:
            json.dump(settings_dict, file, ensure_ascii=False, indent=4)

    def load_settings(self):
        with open("settings.json", 'r', encoding='utf-8') as file:
            settings_dict = json.load(file)
            self.__language = settings_dict['language']
            self.__screenshot_key = settings_dict['screenshot_key']
            self.__resolution = settings_dict["resolution"]
            self.__logos_path = settings_dict["logos_path"]
            self.__unit_names_path = settings_dict["unit_names_path"]

    def load_languages(self):
        self.__text_languages = {}

        with open("languages.json", 'r', encoding='utf-8') as file:
            self.__text_languages = json.load(file)

    def __init__(self):
        self.load_settings()
        self.load_languages()
        self.change_units_dict(False, False)

        # out checker loop vars
        self.__result_lock = threading.Lock()
        self.__image = None
        self.__predicted_units_data = []
        self.__results_is_changed = False
        self.__status = "input_wait"

        # in checker loop vars
        self.__input_lock = threading.Lock()
        self.__results_is_currected = False
        self.__own_br = None

        self.__text_reader = TextReader(self.__logos_path)
        self.__text_reader.screen_resolution = self.__resolution

    def start(self):
        self.__root = Tk()
        self.__root.title("BR checker")

        self._create_widgets()
        self._show_results()

        checker_thread = threading.Thread(target=self.checker_loop)
        checker_thread.daemon = True
        checker_thread.start()

        self.__root.mainloop()

    def _validate_own_br(self, value):
        if not value:
            return True
        for char in value:
            if not (char.isdigit() or char == "."):
                return False
        return value.count(".") <= 1

    def _create_widgets(self):
        Label(
            self.__root, text=self.__text_languages[self.__language]["screenshot_key"]).pack()

        self.__screenshot_key_entry = Entry(self.__root, validate="key")
        self.__screenshot_key_entry.configure(validatecommand=(
            self.__root.register(lambda value: len(value) <= 1), "%P"))
        self.__screenshot_key_entry.pack()
        self.__screenshot_key_entry.insert(0, self.__screenshot_key)

        Label(self.__root,
              text=self.__text_languages[self.__language]["own_br"]).pack()

        self.__own_br_entry = Entry(self.__root, validate="key")
        self.__own_br_entry.configure(validatecommand=(
            self.__root.register(self._validate_own_br), "%P"))
        self.__own_br_entry.pack()

        self.__selected_resolution = StringVar(value=self.__resolution)
        self.__resolution_menu = OptionMenu(
            self.__root, self.__selected_resolution, "1920x1080")
        self.__resolution_menu.pack(pady=10)

        self.__selected_language = StringVar(value=self.__language)
        self.__language_menu = OptionMenu(
            self.__root, self.__selected_language, 'ru', 'eng')
        self.__language_menu.pack(pady=10)

        self.__selected_vehicle_type = StringVar(
            value=self.__text_languages[self.__language]["vehicle_type"])
        self.__vehicle_type_menu = OptionMenu(
            self.__root, self.__selected_vehicle_type, 'plane', 'tank')
        self.__vehicle_type_menu.pack(pady=10)

        self.__status_text = Label(self.__root, text=self.__text_languages[self.__language][self.__status]['text'],
                                   foreground=self.__text_languages[self.__language][self.__status]['color'])
        self.__status_text.pack()

        self.__max_br_text = Label(self.__root, text='')
        self.__max_br_text.pack()

        self.__min_br_text = Label(self.__root, text='')
        self.__min_br_text.pack()

        Button(self.__root, text=self.__text_languages[self.__language]
               ["apply_button"], command=self._apply_button, background="green3").pack()

        self.__image_label = Label(self.__root)
        self.__image_label.pack(side="left", fill="both", expand=True)

        self.__text_frame = Frame(self.__root)
        self.__text_frame.pack(side="right", fill="both", expand=True)

    def _apply_button(self):
        with self.__input_lock:
            self.__screenshot_key = self.__screenshot_key_entry.get()
            try:
                self.__own_br = float(self.__own_br_entry.get())
            except:
                self.__own_br = 0.0

            self.__resolution = self.__selected_resolution.get()
            self.__language = self.__selected_language.get()
            self.save_settings()

            vehicle_type_str = self.__selected_vehicle_type.get()

            self.change_units_dict(True if vehicle_type_str == "plane" else False,
                                   True if vehicle_type_str == "tank" else False)

    def _currect_predicted_data(self):
        currected_names = []
        for entry in self.__text_frame.winfo_children():
            try:
                currected_names.append(entry.get())
            except:
                print("Widget is not entry")

        with self.__result_lock:
            self.__predicted_units_data = [{curr_name: list(unit_data.values())[
                0]} for curr_name, unit_data in zip(currected_names, self.__predicted_units_data)]
        with self.__input_lock:
            self.__results_is_currected = True

    def scan_team_tab(self) -> tuple:
        width, height = map(
            int, self.__text_reader.screen_resolution.split("x"))
        screenshot = np.array(ImageGrab.grab(bbox=(0, 0, width, height)))

        predicted_names = self.__text_reader.read_table(screenshot)

        name_box = TextReader.get_unit_name_box(
            self.__text_reader.screen_resolution)
        left_coord = [name_box[0], name_box[1]]
        right_coord = [name_box[0] + name_box[2],
                       name_box[1] + 16 * name_box[3]]  # 16 players
        cropped_img = screenshot[left_coord[1]                                 : right_coord[1], left_coord[0]: right_coord[0]]

        return predicted_names, cropped_img

    def predict_units_data(self, readed_names: list, own_br: float, units_data: dict) -> list[dict]:

        grabber = UnitGrabber(units_data)
        pred_datas = []
        for name in readed_names:
            if len(name) < 2:
                pred_datas.append({name: None})
                continue
            pred_data = list(grabber.get_unit_br(name, own_br))
            pred_data[0] = '' if pred_data[0] is None else pred_data[0]
            pred_datas.append({pred_data[0]: pred_data[1]})
        return pred_datas

    def _create_dynamic_entrys(self):

        for widget in self.__text_frame.winfo_children():
            widget.destroy()

        row_height = TextReader.get_unit_name_box(self.__resolution)[3]

        for data in self.__predicted_units_data:
            key = list(data.keys())[0]
            br = list(data.values())[0]

            entry = Entry(
                self.__text_frame,
                font=("Arial", 10),
                justify="left"
            )
            if br is None:
                entry.config(background="firebrick1")
            else:
                entry.config(background="lime green")
            entry.insert(0, key)  # Заполняем поле ключом
            entry.pack(fill="x", pady=(
                0, row_height - entry.winfo_reqheight()))

    def _show_team_tab(self):
        img_pil = Image.fromarray(self.__image)
        self.__image_label.config(anchor="ne")
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.__image_label.configure(image=img_tk)
        self.__image_label.image = img_tk

    def _show_BR_text(self):
        battle_ratings = [list(unit_data.values())[
            0] for unit_data in self.__predicted_units_data if list(unit_data.values())[0] != None]

        if len(battle_ratings):
            self.__max_br_text.config(
                text=self.__text_languages[self.__language]["max_br"] + str(max(battle_ratings)))
            self.__min_br_text.config(
                text=self.__text_languages[self.__language]["min_br"] + str(min(battle_ratings)))

    def _show_results(self):
        with self.__result_lock:
            self._show_status_text()

            if not self.__results_is_changed:
                self.__root.after(200, self._show_results)
                return
            self.__results_is_changed = False

            self._show_team_tab()
            self._show_BR_text()
            self._create_dynamic_entrys()

            button = Button(
                self.__text_frame,
                text=self.__text_languages[self.__language]["apply_unit_data"],
                command=self._currect_predicted_data,
                background="green3"
            )
            button.pack(side="right", fill="x", expand=True)

        self.__root.after(100, self._show_results)

    def _show_status_text(self):
        self.__status_text.config(text=self.__text_languages[self.__language][self.__status]['text'],
                                  foreground=self.__text_languages[self.__language][self.__status]['color'])

    def checker_loop(self):
        while True:
            data_is_updated = False
            with self.__input_lock:
                screenshot_key = self.__screenshot_key
                data_is_updated = self.__results_is_currected
                if data_is_updated:
                    self.__results_is_currected = False

            if screenshot_key == '':
                continue

            key_is_pressed = keyboard.is_pressed(screenshot_key)

            if data_is_updated or key_is_pressed:
                with self.__input_lock:
                    units = self.__units
                    self.__text_reader.screen_resolution = self.__resolution
                    own_br = self.__own_br
                with self.__result_lock:
                    self.__status = "in_process"
            else:
                time.sleep(0.010)
                continue

            pred_names = []
            if data_is_updated:
                with self.__result_lock:
                    pred_names = [list(unit_data.keys())[0]
                                  for unit_data in self.__predicted_units_data]
            if key_is_pressed:
                pred_names, screenshot = self.scan_team_tab()

            pred_datas = self.predict_units_data(pred_names, own_br, units)
            print(pred_datas)
            with self.__result_lock:
                self.__predicted_units_data = pred_datas
                self.__results_is_changed = True
                self.__status = "input_wait"

                if key_is_pressed:
                    self.__image = screenshot


def main():
    print(
        """
        WAR BOMBING v1.0
        developed by Leonov Z
    """)

    br_checker = BrChecker()
    br_checker.start()


if __name__ == "__main__":
    main()
