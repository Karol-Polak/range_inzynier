import customtkinter as ctk


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

    #do poprawy
    # def toggle_theme(self):
    #     mode = ctk.get_appearance_mode()
    #     if mode == "dark":
    #         ctk.set_appearance_mode("light")
    #         mode = "light"
    #     else:
    #         ctk.set_appearance_mode("dark")
    #         mode = "dark"