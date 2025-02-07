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

    def update_image(self, image_x=None, image_y=None):
        """
        Aktualizuje obraz na canvasie, tworząc nowy obiekt obrazu przy
        podanych współrzędnych. Jeśli współrzędne nie są podane, pobierane są
        z aktualnego stanu canvasu lub ustawiane na środek canvas.
        """

        if self.original_image is None:
            print("Error: No image loaded in update_image()!")
            return

        # Obliczenie nowego rozmiaru obrazu
        new_size = (int(self.original_image.width * self.zoom_factor),
                    int(self.original_image.height * self.zoom_factor))

        # Przeskalowanie obrazu
        resized_image = self.original_image.resize(new_size, Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)

        # Ustalenie współrzędnych: jeśli nie podano, ustawiamy środek canvas
        if image_x is None or image_y is None:
            if hasattr(self, 'image_id') and self.image_id is not None:
                image_coords = self.image_canvas.coords(self.image_id)
                if image_coords:
                    image_x, image_y = image_coords
                else:
                    image_x, image_y = self.image_canvas.winfo_width() // 2, self.image_canvas.winfo_height() // 2
            else:
                image_x, image_y = self.image_canvas.winfo_width() // 2, self.image_canvas.winfo_height() // 2

        # Zapisujemy środek obrazu (używany przy przeliczaniu trafień)
        self.image_center = (image_x, image_y)

        # Usuwamy stary obraz, jeśli istnieje
        if hasattr(self, 'image_id') and self.image_id is not None:
            self.image_canvas.delete(self.image_id)

        # Tworzymy nowy obraz przy podanych współrzędnych
        self.image_id = self.image_canvas.create_image(image_x, image_y, anchor="center", image=self.photo)

        # Rysujemy na nowo inne elementy (np. trafienia)
        self.redraw_hits()

    def zoom_in(self):
        self.zoom_image(zoom_in=True)

    def zoom_out(self):
        self.zoom_image(zoom_in=False)

    def zoom_image(self, zoom_in=True):
        """
        Zoomuje obraz względem środka canvas – punkt odpowiadający środkowi canvas
        pozostaje w tym samym miejscu. Obliczamy nowe współrzędne obrazu i
        przekazujemy je do update_image(), aby nowy obraz był utworzony w odpowiednim miejscu.
        """

        # Ustalenie skali zoomu
        scale_factor = 1.1 if zoom_in else 0.9

        # Sprawdzenie zakresu zoomu
        if not (self.min_zoom < self.zoom_factor * scale_factor < self.max_zoom):
            return

        # Pobranie wymiarów canvasu i obliczenie jego środka
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        canvas_center_x = canvas_width // 2
        canvas_center_y = canvas_height // 2

        # Upewnienie się, że canvas został zaktualizowany
        self.image_canvas.update_idletasks()

        # Pobranie aktualnych współrzędnych obrazu (zakładamy anchor "center")
        if hasattr(self, 'image_id') and self.image_id is not None:
            coords = self.image_canvas.coords(self.image_id)
            if coords:
                image_x, image_y = coords[0], coords[1]
            else:
                bbox = self.image_canvas.bbox(self.image_id)
                if bbox:
                    image_x = (bbox[0] + bbox[2]) / 2
                    image_y = (bbox[1] + bbox[3]) / 2
                else:
                    print("Error: Image coordinates not found!")
                    return
        else:
            print("Error: No image loaded!")
            return

        # Obliczenie nowych współrzędnych obrazu względem środka canvas
        new_x = canvas_center_x + (image_x - canvas_center_x) * scale_factor
        new_y = canvas_center_y + (image_y - canvas_center_y) * scale_factor

        # Aktualizacja zoomu
        self.zoom_factor *= scale_factor

        # Wywołanie update_image() z nowymi współrzędnymi
        self.update_image(new_x, new_y)

    def add_hit(self, event):
        if not self.image_path:
            messagebox.showerror("Błąd", "Najpierw wczytaj obraz!")
            return

        # Pobieramy środek obrazu – zakładamy, że jest zapisany w self.image_center
        if hasattr(self, 'image_center'):
            center_x, center_y = self.image_center
        else:
            center_x, center_y = self.image_canvas.winfo_width() // 2, self.image_canvas.winfo_height() // 2

        original_width = self.original_image.width
        original_height = self.original_image.height

        # Przeliczamy współrzędne kliknięcia (canvas) na współrzędne w oryginalnym obrazie
        original_hit_x = (event.x - center_x) / self.zoom_factor + (original_width / 2)
        original_hit_y = (event.y - center_y) / self.zoom_factor + (original_height / 2)

        self.hit_coordinates.append((original_hit_x, original_hit_y))

        # Aby od razu narysować trafienie, przeliczamy je z powrotem na współrzędne canvasu:
        canvas_hit_x = center_x + (original_hit_x - (original_width / 2)) * self.zoom_factor
        canvas_hit_y = center_y + (original_hit_y - (original_height / 2)) * self.zoom_factor

        self.draw_hit(canvas_hit_x, canvas_hit_y)

    def draw_hit(self, x, y):
        r = 5
        self.image_canvas.create_oval(x - r, y - r, x + r, y + r, fill="red", outline="black")

    def redraw_hits(self):
        # Ustalanie środka obrazu – przyjmujemy, że został zapisany w update_image()
        if hasattr(self, 'image_center'):
            center_x, center_y = self.image_center
        else:
            center_x, center_y = self.image_canvas.winfo_width() // 2, self.image_canvas.winfo_height() // 2

        original_width = self.original_image.width
        original_height = self.original_image.height

        # Iterujemy po trafieniach, przeliczając współrzędne z układu oryginalnego obrazu
        for original_hit_x, original_hit_y in self.hit_coordinates:
            canvas_hit_x = center_x + (original_hit_x - (original_width / 2)) * self.zoom_factor
            canvas_hit_y = center_y + (original_hit_y - (original_height / 2)) * self.zoom_factor
            self.draw_hit(canvas_hit_x, canvas_hit_y)

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

        try:
            detected_hits = detect_hits(self.image_path, debug=False, save_debug=True)

            if detected_hits:
                # Przekształcamy współrzędne na względne (procentowe)
                img_width, img_height = self.original_image.size
                self.hit_coordinates = [(x / img_width, y / img_height) for x, y in detected_hits]
                self.redraw_hits()
                messagebox.showinfo("Sukces", f"Wykryto {len(detected_hits)} trafień.")
            else:
                messagebox.showinfo("Brak trafień", "Nie wykryto żadnych trafień na obrazie.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wykryć trafień: {e}")

