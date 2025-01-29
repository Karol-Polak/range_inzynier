from gui.main_window import MainWindow
from logic.data_manager import initialize_database
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="customtkinter")

if __name__ == "__main__":
    initialize_database()
    app = MainWindow()
    app.run()
