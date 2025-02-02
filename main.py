from gui.main_window import MainWindow
from logic.data_manager import initialize_database
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="customtkinter")

if __name__ == "__main__":
    try:
        initialize_database()
    except Exception as e:
        print("Błąd przy inicjalizacji bazy danych:", e)
        exit(1)

    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print("Wystąpił błąd podczas działania aplikacji:", e)
