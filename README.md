# 🎯 Aplikacja do Analizy Trafień na Tarczy

## 📌 Opis Projektu
Aplikacja umożliwia analizę trafień na tarczy strzeleckiej. Użytkownik może wczytać obraz tarczy, a następnie skorzystać z automatycznej detekcji przestrzelin. Algorytmy wykrywają okrągłe kształty odpowiadające trafieniom i eliminują fałszywe oznaczenia (np. cyfry na tarczy). 

Aplikacja obsługuje również funkcję ręcznego dodawania trafień oraz zoomowania i przesuwania obrazu w celu dokładnej analizy.

---

## 🚀 Funkcjonalności
✅ Wczytywanie obrazu tarczy (obsługa plików PNG, JPG, JPEG)  
✅ Automatyczne wykrywanie trafień metodą Hougha  
✅ Ignorowanie cyfr na tarczy (OCR + filtracja)  
✅ Możliwość ręcznego dodawania i usuwania trafień  
✅ Zoomowanie i przesuwanie tarczy  
✅ Obsługa różnych rodzajów tarcz strzeleckich  
✅ Wsparcie dla eksportu wyników  

---

## 🔧 Instalacja
### **1️⃣ Wymagania systemowe**
- Python 3.8+
- System: Windows / macOS / Linux

### **2️⃣ Klonowanie repozytorium**
```sh
git clone https://github.com/TwojeRepozytorium/analiza-trafien.git
cd analiza-trafien
```

### **3️⃣ Instalacja zależności**
Użyj **pip** do zainstalowania wymaganych pakietów:
```sh
pip install -r requirements.txt
```

---

## 🎯 Uruchomienie aplikacji
```sh
python main.py
```

Jeśli używasz **virtualenv**, najpierw aktywuj środowisko:
```sh
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate    # Windows
python main.py
```

---

## ⚙️ Struktura projektu
```
📂 range_inzynier
├── 📁 assets
├── ── 📁 images
├── 📁 database
├── ── 📁 results.db
├── 📁 gui                
│   ├── ___init___.py  
│   ├── add_training_view.py
│   ├── analysis_view.py
│   ├── history_view.py
│   ├── main_window.py
│   ├── ready_training_view.py
│   └── settings_view.py   
├── 📁 logic                  
│   ├── ___init___.py
│   ├── data_manager.py
│   ├── image_analysis.py
│   ├── image_handler.py   
│   ├── statistics.py       
│   └── validation.py  
├── main.py                
├── config.txt       
└── README.md              
```

---

## 🖼️ Jak działa wykrywanie trafień?
1️⃣ Obraz jest konwertowany do skali szarości i rozmywany.
2️⃣ Metoda **HoughCircles** wykrywa potencjalne trafienia.
3️⃣ Algorytm **OCR (Tesseract)** wykrywa cyfry i tworzy maskę.
4️⃣ Trafienia pokrywające się z cyframi są ignorowane.
5️⃣ Dodatkowa analiza kształtu i tekstury eliminuje błędne detekcje.

---
