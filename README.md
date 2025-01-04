# war-thunder-br-checker
Программа для определения макимального и минимального БР.

![Screenshot 2025-01-02 204012](https://github.com/user-attachments/assets/79e4f771-62e4-465a-83ba-307522663b39)



ЗАПУСК:
1. Установите Python 3.10+
2. В cmd установите необходимые библиотеки:
   
   pip install opencv-python
   
   pip install Pillow
   
   pip install keyboard
   
   pip install pytesseract
   
   pip install Levenshtein
   
   pip install selenium
   
   pip install beautifulsoup4
   
3. Далее устаналиваем Tesseract-OCR и вводим путь к tesseract.exe в переменные среды
   https://github.com/tesseract-ocr/tesseract/releases
4. Запускаем файл br_checker.py и фиксим ошибки если возникли.
5. Приложение готово

Использование:
1. Обязательно переключаем раскладку на англиский язык
2. Запускаем br_checker.py и вводим свои данные
3. Запускаем War Thunder(можно  и до запуска программы)
4. Входим в воздушный или в танковый бой
5. Прожимаем кнопку активации
6. Переходим в приложение и корректируем навзания техники
7. Получаем максимальный и минимальный БР

Ввод своего разрешения экрана
1. Откройте br_checker.py через любой редактор.
2. В строчке где написано self.__resolution_menu = OptionMenu(self.__root, self.__selected_resolution ,"1920x1080") после "1920x1080" поставте запятую и в кавычках напишите разрешение
3. Откройте Text_Reader/text_reader.py через любой редактор.
4. в функции get_unit_name_box добавте своё разрешение по аналогии с 1920x1080
5. Занчение должно быть такое (x, y, ширина, высота) обозначает квадрат в который заключен название первой техники в таблице
