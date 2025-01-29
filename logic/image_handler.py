import shutil
import os
from customtkinter import CTkImage
from PIL import Image

def load_image(filepath, size=(600, 600)):
    """Ładuje obraz jako CTkImage w zadanym rozmiarze."""
    img = Image.open(filepath)
    img = img.resize(size)
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
