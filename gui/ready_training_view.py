import customtkinter as ctk
from training_data.training_drills import TRAININGS_DATA


class ReadyTrainingView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Nagłówek widoku
        header_label = ctk.CTkLabel(self, text="Propozycje Treningów", font=("Arial", 20))
        header_label.pack(pady=10)

        # Kombobox do wyboru typu broni
        self.weapon_combobox = ctk.CTkComboBox(
            self,
            values=["Pistolet", "Karabin", "Strzelba"],
            command=self.weapon_selected
        )
        self.weapon_combobox.pack(pady=10, padx=10)

        # Kontener na kafelki – CTkScrollableFrame
        self.cards_container = ctk.CTkScrollableFrame(
            self,
            width=800,
            height=600,
            corner_radius=10,
            border_color=("gray70", "gray40"),
            border_width=2
        )
        self.cards_container.pack(pady=10, padx=10, fill="both", expand=True)

    def weapon_selected(self, weapon):
        # Czyścimy poprzednie kafelki
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        # Pobieramy listę treningów
        trainings = self.get_trainings_for_weapon(weapon)

        # Tworzymy kafelki
        for training in trainings:
            self.create_training_card(self.cards_container, training)

    def get_trainings_for_weapon(self, weapon):
        return TRAININGS_DATA.get(weapon.lower(), [])

    def create_training_card(self, parent, training_data):
        card_frame = ctk.CTkFrame(
            parent,
            corner_radius=10,
            border_color=("gray70", "gray40"),
            border_width=1,
            fg_color=("gray90", "gray15")
        )
        card_frame.pack(pady=10, padx=10, fill="x")

        # Tytuł - większa, pogrubiona czcionka
        title_label = ctk.CTkLabel(
            card_frame,
            text=training_data["title"],
            font=("Arial", 16, "bold"),
            text_color=("black", "white")
        )
        title_label.pack(pady=(10, 5), padx=10, anchor="w")

        # Skrócony opis - mniejsza czcionka
        short_desc_label = ctk.CTkLabel(
            card_frame,
            text=training_data["short_description"],
            justify="left",
            wraplength=700
        )
        short_desc_label.pack(pady=(0, 10), padx=10, anchor="w")

        # Przycisk "Więcej"
        more_button = ctk.CTkButton(
            card_frame,
            text="Więcej",
            command=lambda: self.show_training_details(training_data)
        )
        more_button.pack(pady=(0, 10), padx=10, anchor="e")

    def show_training_details(self, training_data):
        # Nowe okno z pełnym opisem
        details_window = ctk.CTkToplevel(self)
        details_window.title(training_data["title"])
        details_window.geometry("600x400")

        title_label = ctk.CTkLabel(
            details_window,
            text=training_data["title"],
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=10)

        full_desc_label = ctk.CTkLabel(
            details_window,
            text=training_data["full_description"],
            justify="left",
            wraplength=580
        )
        full_desc_label.pack(pady=10, padx=10, fill="both", expand=True)
