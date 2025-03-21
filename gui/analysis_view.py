import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

from logic.image_analysis import detect_hits_with_text_filter
from logic.data_manager import fetch_all_trainings


class AnalysisView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.hit_coordinates = []
        self.adding_hits_mode = False
        self.zoom_factor = 1.0
        self.min_zoom = 0.2
        self.max_zoom = 3.0

        # -- Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=1)

        # Sekcja 1: Wybór sesji
        self.session_frame = ctk.CTkFrame(self, border_width=2)
        self.session_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        session_values = self.get_session_list()
        self.session_selector = ctk.CTkComboBox(self.session_frame, values=session_values)
        self.session_selector.pack(pady=5, padx=10, fill="x")

        self.load_session_button = ctk.CTkButton(
            self.session_frame, text="🔄 Wczytaj sesję", command=self.load_session_image
        )
        self.load_session_button.pack(pady=5, padx=10, fill="x")

        self.upload_external_button = ctk.CTkButton(
            self.session_frame, text="📂 Wczytaj obraz", command=self.upload_external_image
        )
        self.upload_external_button.pack(pady=5, padx=10, fill="x")

        # Sekcja 2: Narzędzia
        self.tools_frame = ctk.CTkFrame(self, border_width=2)
        self.tools_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.add_hits_button = ctk.CTkButton(
            self.tools_frame, text="🎯 Dodaj trafienia", command=self.toggle_add_hits_mode
        )
        self.add_hits_button.pack(side="left", padx=5, pady=5)

        self.clear_hits_button = ctk.CTkButton(
            self.tools_frame, text="❌ Wyczyść trafienia", command=self.clear_hits
        )
        self.clear_hits_button.pack(side="left", padx=5, pady=5)

        self.detect_hits_button = ctk.CTkButton(
            self.tools_frame, text="🔍 Wykryj trafienia", command=self.detect_hits, state="disabled"
        )
        self.detect_hits_button.pack(side="left", padx=5, pady=5)

        # Sekcja 3: Zoom
        self.zoom_frame = ctk.CTkFrame(self, border_width=2)
        self.zoom_frame.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

        self.zoom_in_button = ctk.CTkButton(self.zoom_frame, text="🔍 +", command=self.zoom_in, width=30)
        self.zoom_in_button.pack(side="left", padx=5, pady=5)

        self.zoom_out_button = ctk.CTkButton(self.zoom_frame, text="🔍 -", command=self.zoom_out, width=30)
        self.zoom_out_button.pack(side="left", padx=5, pady=5)

        # Obszar Canvas
        self.image_canvas = ctk.CTkCanvas(self, width=800, height=800)
        self.image_canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # Obsługa myszy
        self.image_canvas.bind("<ButtonPress-1>", self.start_move)
        self.image_canvas.bind("<B1-Motion>", self.do_move)

        # Zmienne
        self.image_path = None
        self.photo = None
        self.original_image = None
        self.canvas_drag_data = {"x": 0, "y": 0}
        self.image_id = None
        self.image_center = None

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
        self.original_image = pil_image
        self.zoom_factor = 1.0
        self.update_image()

        # Wymuszenie odświeżenia
        self.image_canvas.update_idletasks()
        self.image_canvas.update()

        self.detect_hits_button.configure(state="normal")

    def update_image(self, image_x=None, image_y=None):
        if self.original_image is None:
            print("Error: No image loaded in update_image()!")
            return

        new_size = (
            int(self.original_image.width * self.zoom_factor),
            int(self.original_image.height * self.zoom_factor)
        )

        resized_image = self.original_image.resize(new_size, Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)

        if image_x is None or image_y is None:
            if self.image_id is not None:
                coords = self.image_canvas.coords(self.image_id)
                if coords:
                    image_x, image_y = coords
                else:
                    image_x, image_y = self.image_canvas.winfo_width()//2, self.image_canvas.winfo_height()//2
            else:
                image_x, image_y = self.image_canvas.winfo_width()//2, self.image_canvas.winfo_height()//2

        self.image_center = (image_x, image_y)

        if self.image_id is not None:
            self.image_canvas.delete(self.image_id)

        self.image_id = self.image_canvas.create_image(image_x, image_y, anchor="center", image=self.photo)

        # Odświeżenie
        self.image_canvas.update_idletasks()
        self.image_canvas.update()

        self.redraw_hits()

    def zoom_in(self):
        self.zoom_image(True)

    def zoom_out(self):
        self.zoom_image(False)

    def zoom_image(self, zoom_in=True):
        scale_factor = 1.1 if zoom_in else 0.9
        if not (self.min_zoom < self.zoom_factor * scale_factor < self.max_zoom):
            return

        self.image_canvas.update_idletasks()
        self.image_canvas.update()

        if self.image_id is not None:
            coords = self.image_canvas.coords(self.image_id)
            if coords:
                image_x, image_y = coords
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

        new_x = self.image_canvas.winfo_width()//2 + (image_x - self.image_canvas.winfo_width()//2)*scale_factor
        new_y = self.image_canvas.winfo_height()//2 + (image_y - self.image_canvas.winfo_height()//2)*scale_factor

        self.zoom_factor *= scale_factor
        self.update_image(new_x, new_y)

    def add_hit(self, event):
        if not self.image_path:
            messagebox.showerror("Błąd", "Najpierw wczytaj obraz!")
            return

        if self.image_center is None:
            cx = self.image_canvas.winfo_width()//2
            cy = self.image_canvas.winfo_height()//2
        else:
            cx, cy = self.image_center

        orig_w = self.original_image.width
        orig_h = self.original_image.height

        # Oryginalne współrzędne
        x_orig = (event.x - cx)/self.zoom_factor + (orig_w/2)
        y_orig = (event.y - cy)/self.zoom_factor + (orig_h/2)

        self.hit_coordinates.append((x_orig, y_orig))

        self.redraw_hits()

    def draw_hit(self, x, y):
        r = 5
        self.image_canvas.create_oval(
            x - r, y - r, x + r, y + r, fill="red", outline="black", tags="hit"
        )

    def redraw_hits(self):
        if not self.hit_coordinates or not self.image_id:
            return

        self.image_canvas.delete("hit")

        cx, cy = self.image_center if self.image_center else (self.image_canvas.winfo_width()//2,
                                                              self.image_canvas.winfo_height()//2)
        orig_w, orig_h = self.original_image.size

        # Przeliczenie oryginalnych współrzędnych (x_orig, y_orig) na Canvas
        for (x_orig, y_orig) in self.hit_coordinates:
            x_canvas = cx + (x_orig - (orig_w/2)) * self.zoom_factor
            y_canvas = cy + (y_orig - (orig_h/2)) * self.zoom_factor
            self.draw_hit(x_canvas, y_canvas)

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
        if not self.image_path:
            messagebox.showerror("Błąd", "Najpierw wczytaj obraz!")
            return

        try:
            # Wykrycie trafień w oryginalnym obrazie
            circles = detect_hits_with_text_filter(self.image_path)
            if circles:
                # Zapisujemy w oryginalnym układzie
                self.hit_coordinates = [(x, y) for x, y, r in circles]
                self.redraw_hits()
                messagebox.showinfo("Sukces", f"Wykryto {len(circles)} trafień.")
            else:
                messagebox.showinfo("Brak trafień", "Nie wykryto żadnych trafień na obrazie.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wykryć trafień: {e}")
