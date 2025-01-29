import shutil
import os
from customtkinter import CTkImage
from PIL import Image


def load_image(filepath, max_width, max_height):
    """Ładuje obraz i skaluje go proporcjonalnie do podanych maksymalnych wymiarów."""
    img = Image.open(filepath)
    img_width, img_height = img.size

    # Oblicz współczynnik skalowania
    scale = min(max_width / img_width, max_height / img_height)
    new_size = (int(img_width * scale), int(img_height * scale))

    img = img.resize(new_size, Image.Resampling.LANCZOS)
    return CTkImage(img)



def save_image_locally(image_path):
    # Docelowa lokalizacja obrazów
    target_folder = "assets/images"
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # Kopiowanie obrazu
    file_name = os.path.basename(image_path)  # Pobranie nazwy pliku
    target_path = os.path.join(target_folder, file_name)
    shutil.copy(image_path, target_path)

    return target_path
