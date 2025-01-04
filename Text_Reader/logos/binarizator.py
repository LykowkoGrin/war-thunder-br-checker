import cv2
import numpy as np
import os


def binarize_images_in_folder(folder_path):

    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            file_path = os.path.join(folder_path, filename)
            # Загрузка изображения
            image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                print(f"Не удалось загрузить изображение: {filename}")
                continue

            # Бинаризация изображения
            _, binary_image = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY)

            # Сохранение бинарного изображения
            cv2.imwrite(file_path, binary_image)
            print(f"Бинаризованное изображение сохранено: {filename}")


if __name__ == "__main__":
    binarize_images_in_folder('Text_Reader/logos')
