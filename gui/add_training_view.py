import customtkinter as ctk
from tkinter import filedialog
from logic.validation import validate_training_data
from logic.data_manager import save_training_to_db
from logic.image_handler import load_image
from logic.image_handler import save_image_locally

# import do walidacji wpisanych danych
from logic.data_manager import get_last_training

class AddTrainingView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.header_label = ctk.CTkLabel(self, text="Dodaj nowy trening", font=("Arial", 20))
        self.header_label.pack(pady=10)

        self.message_label = ctk.CTkLabel(self, text="", text_color="green")
        self.message_label.pack(pady=10)

        # Formularz
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=10, padx=10, fill="x")

        # Pola formularza
        self.distance_entry = self.create_entry("Dystans (m):", 0)
        self.shots_entry = self.create_entry("Liczba strzałów:", 1)
        self.target_combobox = self.create_combobox("Typ tarczy:", ["Klasyczna", "Sylwetka", "Dynamiczna"], 2)

        # Wczytywanie zdjęcia
        self.image_label = ctk.CTkLabel(self, text="Brak wczytanego obrazu")
        self.image_label.pack(pady=10)
        self.upload_button = ctk.CTkButton(self, text="Wczytaj zdjęcie tarczy", command=self.upload_image)
        self.upload_button.pack(pady=10)

        # Przycisk zapisu
        self.save_button = ctk.CTkButton(self, text="Zapisz trening", command=self.save_training)
        self.save_button.pack(pady=20)

        self.image_path = None

    def create_entry(self, label_text, row):
        label = ctk.CTkLabel(self.form_frame, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        entry = ctk.CTkEntry(self.form_frame, placeholder_text="...")
        entry.grid(row=row, column=1, padx=10, pady=5)
        return entry

    def create_combobox(self, label_text, values, row):
        label = ctk.CTkLabel(self.form_frame, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        combobox = ctk.CTkComboBox(self.form_frame, values=values)
        combobox.grid(row=row, column=1, padx=10, pady=5)
        return combobox

    def upload_image(self):
        filetypes = [("Pliki graficzne", "*.png *.jpg *.jpeg"), ("Wszystkie pliki", "*.*")]
        filepath = filedialog.askopenfilename(title="Wybierz obraz tarczy", filetypes=filetypes)
        if filepath:
            self.image_path = filepath
            photo = load_image(filepath)
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo

    def save_training(self):
        distance = self.distance_entry.get()
        shots = self.shots_entry.get()
        target_type = self.target_combobox.get()

        # Walidacja danych
        errors = validate_training_data(distance, shots, self.image_path)
        if errors:
            self.message_label.configure(text="Błąd: " + ", ".join(errors), text_color="red")
            return

        # Walidacja obrazu
        if not self.image_path:
            self.message_label.configure(text="Błąd: Brak wczytanego obrazu!", text_color="red")
            return

        # Kopiowanie obrazu do folderu i zapis ścieżki
        saved_path = save_image_locally(self.image_path)

        # Zapis danych do bazy
        save_training_to_db(distance, shots, target_type, saved_path)

        # Wyświetlenie komunikatu sukcesu
        self.message_label.configure(text="Sukces: Trening został zapisany!", text_color="green")

        # Czyszczenie formularza
        self.distance_entry.delete(0, "end")
        self.shots_entry.delete(0, "end")
        self.target_combobox.set("")
        self.image_path = None
        self.image_label.configure(image=None, text="Brak wczytanego obrazu")

        # Walidacja wpisanych danych - do usuniecia
        last_training = get_last_training()
        print("Ostatni zapis:", last_training)
