import customtkinter as ctk
from gui.add_training_view import AddTrainingView
from gui.analysis_view import AnalysisView
from gui.history_view import HistoryView
from gui.settings_view import SettingsView
from gui.ready_training_view import ReadyTrainingView
from config import current_theme

class MainWindow:
    def __init__(self):
        # Motyw główny
        ctk.set_default_color_theme("dark-blue")
        ctk.set_appearance_mode(current_theme)


        self.app = ctk.CTk()
        self.app.title("Aplikacja do analizy trafień")
        self.app.geometry("1050x950")

        # Nagłówek
        header_label = ctk.CTkLabel(self.app, text="Aplikacja do analizy trafień", font=("Arial", 24))
        header_label.pack(pady=20)

        # Menu boczne
        self.menu_frame = ctk.CTkFrame(self.app, width=200, corner_radius=10)
        self.menu_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.content_frame = ctk.CTkFrame(self.app, corner_radius=10)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Przyciski menu
        self.create_menu_buttons()

        # Domyślna zawartość
        self.show_view(AddTrainingView)

    def create_menu_buttons(self):
        buttons = [
            ("Dodaj trening", AddTrainingView),
            ("Analiza wyników", AnalysisView),
            ("Historia treningów", HistoryView),
            ("Gotowe treningi", ReadyTrainingView),
            ("Ustawienia", SettingsView),
        ]

        for text, view in buttons:
            button = ctk.CTkButton(self.menu_frame, text=text, command=lambda v=view: self.show_view(v))
            button.pack(pady=10, padx=10)

    def show_view(self, view_class):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        view = view_class(self.content_frame)
        view.pack(fill="both", expand=True)

    def run(self):
        self.app.mainloop()
