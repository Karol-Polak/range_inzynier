import sqlite3
import os

def initialize_database(db_path="database/results.db"):
    """Inicjalizuje bazę danych, tworząc tabelę, jeśli nie istnieje."""
    # Sprawdź, czy folder bazy danych istnieje
    folder = os.path.dirname(db_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Połącz się z bazą danych
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Tworzenie tabeli, jeśli nie istnieje
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trainings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            distance INTEGER,
            shots INTEGER,
            target_type TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_training_to_db(distance, shots, target_type, image_path, db_path="database/results.db"):
    """
    Zapisuje dane treningowe do bazy SQLite.
    :param distance: Dystans w metrach
    :param shots: Liczba oddanych strzałów
    :param target_type: Typ tarczy (np. "Klasyczna", "Sylwetka")
    :param image_path: Ścieżka do zdjęcia tarczy w folderze assets/images
    :param db_path: Ścieżka do pliku bazy danych
    """
    # Łączenie z bazą danych
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Wstawianie danych do tabeli
    cursor.execute("""
        INSERT INTO trainings (distance, shots, target_type, image_path)
        VALUES (?, ?, ?, ?)
    """, (distance, shots, target_type, image_path))

    connection.commit()
    connection.close()


def fetch_all_trainings(db_path="database/results.db"):
    """
    Pobiera wszystkie zapisane treningi z bazy danych.
    :param db_path: Ścieżka do pliku bazy danych
    :return: Lista krotek z wynikami treningów
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Pobranie wszystkich treningów
    cursor.execute("SELECT * FROM trainings")
    results = cursor.fetchall()

    connection.close()
    return results


def get_last_training(db_path="database/results.db"):
    """Pobiera ostatnio zapisany trening z bazy danych."""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM trainings
        ORDER BY id DESC
        LIMIT 1
    """)
    result = cursor.fetchone()
    connection.close()
    return result


def clear_database(db_path="database/results.db"):
    """
    Usuwa wszystkie rekordy z tabeli trainings i resetuje licznik id,
    dzięki czemu przy następnym zapisie pierwszy rekord otrzyma id 1.
    """
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Usunięcie rekordów z tabeli trainings
    cursor.execute("DELETE FROM trainings")

    # Resetowanie licznika AUTOINCREMENT w tabeli trainings
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='trainings'")

    connection.commit()
    connection.close()
