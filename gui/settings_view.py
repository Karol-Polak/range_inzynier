import customtkinter as ctk
from config import current_theme

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Nagłówek
        self.header_label = ctk.CTkLabel(self, text="Ustawienia", font=("Arial", 20))
        self.header_label.pack(pady=10)

        # Zmiana motywu
        self.theme_label = ctk.CTkLabel(self, text="Motyw aplikacji:")
        self.theme_label.pack(pady=5)

        self.theme_button = ctk.CTkButton(self, text="Przełącz na tryb jasny", command=self.toggle_theme)
        self.theme_button.pack(pady=10)

    def toggle_theme(self):
        global current_theme
        if current_theme == "dark":
            current_theme = "light"
            ctk.set_appearance_mode("light")
            self.theme_button.configure(text="Przełącz na tryb ciemny")
        else:
            current_theme = "dark"
            ctk.set_appearance_mode("dark")
            self.theme_button.configure(text="Przełącz na tryb jasny")