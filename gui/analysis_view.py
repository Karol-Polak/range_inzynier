import customtkinter as ctk

class AnalysisView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(self, text="Dodaj trening - tutaj będzie formularz", font=("Arial", 16))
        label.pack(pady=20)
