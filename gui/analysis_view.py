import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from logic.image_analysis import detect_hits
from logic.data_manager import fetch_all_trainings


class AnalysisView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.hit_coordinates = []  # Lista trafień
        self.adding_hits_mode = False  # Tryb dodawania trafień
        self.zoom_factor = 1.0
        self.min_zoom = 0.2
        self.max_zoom = 3.0

        #Układ sekcji w grid
        self.grid_columnconfigure(0, weight=1)  # Lewa kolumna (Wybór sesji)
        self.grid_columnconfigure(1, weight=2)  # Środkowa kolumna (Narzędzia)
        self.grid_columnconfigure(2, weight=1)  # Prawa kolumna (Zoom i nawigacja)

        #**Sekcja 1: Wybór sesji**
        self.session_frame = ctk.CTkFrame(self, border_width=2)
        self.session_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        session_values = self.get_session_list()
        self.session_selector = ctk.CTkComboBox(self.session_frame, values=session_values)
        self.session_selector.pack(pady=5, padx=10, fill="x")

        self.load_session_button = ctk.CTkButton(self.session_frame, text="🔄 Wczytaj sesję",
                                                 command=self.load_session_image)
        self.load_session_button.pack(pady=5, padx=10, fill="x")

        self.upload_external_button = ctk.CTkButton(self.session_frame, text="📂 Wczytaj obraz",
                                                    command=self.upload_external_image)
        self.upload_external_button.pack(pady=5, padx=10, fill="x")

        #**Sekcja 2: Narzędzia analizy**
        self.tools_frame = ctk.CTkFrame(self, border_width=2)
        self.tools_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.add_hits_button = ctk.CTkButton(self.tools_frame, text="🎯 Dodaj trafienia",
                                             command=self.toggle_add_hits_mode)
        self.add_hits_button.pack(side="left", padx=5, pady=5)

        self.clear_hits_button = ctk.CTkButton(self.tools_frame, text="❌ Wyczyść trafienia", command=self.clear_hits)
        self.clear_hits_button.pack(side="left", padx=5, pady=5)

        self.detect_hits_button = ctk.CTkButton(self.tools_frame, text="🔍 Wykryj trafienia", command=self.detect_hits)
        self.detect_hits_button.pack(side="left", padx=5, pady=5)

        #**Sekcja 3: Zoom i nawigacja**
        self.zoom_frame = ctk.CTkFrame(self, border_width=2)
        self.zoom_frame.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        self.zoom_in_button = ctk.CTkButton(self.zoom_frame, text="🔍 +", command=self.zoom_in, width=30)
        self.zoom_in_button.pack(side="left", padx=5, pady=5)

        self.zoom_out_button = ctk.CTkButton(self.zoom_frame, text="🔍 -", command=self.zoom_out, width=30)
        self.zoom_out_button.pack(side="left", padx=5, pady=5)

        #**Obszar wyświetlania obrazu**
        self.image_canvas = ctk.CTkCanvas(self, width=800, height=800)
        self.image_canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        #Obsługa zdarzeń myszy
        self.image_canvas.bind("<ButtonPress-1>", self.start_move)
        self.image_canvas.bind("<B1-Motion>", self.do_move)
        self.image_canvas.bind("<MouseWheel>", self.zoom_image)
        self.image_canvas.bind("<Control-MouseWheel>", self.zoom_image)

        #Zmienne do przechowywania obrazu
        self.image_path = None
        self.photo = None
        self.original_image = None
        self.canvas_drag_data = {"x": 0, "y": 0}

    def toggle_add_hits_mode(self):
        self.adding_hits_mode = not self.adding_hits_mode
        if self.adding_hits_mode:
            self.add_hits_button.configure(text="Wyłącz dodawanie trafień")
            self.image_canvas.bind("<Button-1>", self.add_hit)
        else:
            self.add_hits_button.configure(text="Dodaj trafienia")
            self.image_canvas.bind("<ButtonPress-1>", self.start_move)

    def get_session_list(self):
        trainings = fetch_all_trainings()
        session_list = []
        self.sessions = {}
        if trainings:
            for training in trainings:
                session_label = f"Sesja {training[0]} - {training[5]}"
                session_list.append(session_label)
                self.sessions[session_label] = training
        else:
            session_list = ["Brak sesji treningowych"]
            self.sessions = {}
        return session_list

    def load_session_image(self):
        selected = self.session_selector.get()
        if selected not in self.sessions:
            messagebox.showerror("Błąd", "Nie wybrano poprawnej sesji treningowej.")
            return
        training = self.sessions[selected]
        self.image_path = training[4]
        self.hit_coordinates = []
        self.display_image_with_hits(self.image_path, self.hit_coordinates)

    def upload_external_image(self):
        filetypes = [("Pliki graficzne", "*.png *.jpg *.jpeg"), ("Wszystkie pliki", "*.*")]
        filepath = filedialog.askopenfilename(title="Wybierz obraz", filetypes=filetypes)
        if filepath:
            self.image_path = filepath
            self.hit_coordinates = []
            self.display_image_with_hits(filepath, [])

    def display_image_with_hits(self, image_path, hit_coordinates):
        self.image_canvas.delete("all")
        pil_image = Image.open(image_path)
        self.original_image = pil_image  # Zapisz oryginalny obraz
        self.zoom_factor = 1.0  # Reset zoomu
        self.update_image()

        for (x, y) in hit_coordinates:
            self.draw_hit(x, y)

    def update_image(self):
        if self.original_image is None:
            return

        new_size = (
        int(self.original_image.width * self.zoom_factor), int(self.original_image.height * self.zoom_factor))
        resized_image = self.original_image.resize(new_size, Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)

        self.image_canvas.delete("all")
        self.image_canvas.create_image(0, 0, anchor="nw", image=self.photo)

    def zoom_in(self):
        if self.zoom_factor < self.max_zoom:
            self.zoom_factor *= 1.1
            self.update_image()

    def zoom_out(self):
        if self.zoom_factor > self.min_zoom:
            self.zoom_factor *= 0.9
            self.update_image()

    def zoom_image(self, event):
        if event.delta > 0 and self.zoom_factor < self.max_zoom:
            self.zoom_factor *= 1.1
        elif event.delta < 0 and self.zoom_factor > self.min_zoom:
            self.zoom_factor *= 0.9
        self.update_image()

    def add_hit(self, event):
        if not self.image_path:
            messagebox.showerror("Błąd", "Najpierw wczytaj obraz!")
            return

        x, y = event.x, event.y
        self.hit_coordinates.append((x, y))
        self.draw_hit(x, y)

    def draw_hit(self, x, y):
        r = 5
        self.image_canvas.create_oval(x - r, y - r, x + r, y + r, fill="red", outline="black")

    def clear_hits(self):
        self.hit_coordinates = []
        self.update_image()

    def start_move(self, event):
        self.canvas_drag_data["x"] = event.x
        self.canvas_drag_data["y"] = event.y

    def do_move(self, event):
        dx = event.x - self.canvas_drag_data["x"]
        dy = event.y - self.canvas_drag_data["y"]
        self.image_canvas.move("all", dx, dy)
        self.canvas_drag_data["x"] = event.x
        self.canvas_drag_data["y"] = event.y

    def detect_hits(self):
        """
        Wykrywa trafienia na tarczy i oznacza je na obrazie.
        """
        if not self.image_path:
            messagebox.showerror("Błąd", "Najpierw wczytaj obraz!")
            return

        detected_hits = detect_hits(self.image_path)

        if detected_hits:
            self.hit_coordinates = detected_hits
            self.display_image_with_hits(self.image_path, self.hit_coordinates)
        else:
            messagebox.showinfo("Brak trafień", "Nie wykryto żadnych trafień na obrazie.")