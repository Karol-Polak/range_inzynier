def validate_training_data(distance, shots, image_path):
    """Waliduje dane treningowe."""
    errors = []

    if not distance.isdigit():
        errors.append("Dystans musi być liczbą całkowitą.")

    if not shots.isdigit():
        errors.append("Liczba strzałów musi być liczbą całkowitą.")

    if not image_path:
        errors.append("Musisz wczytać zdjęcie tarczy.")

    return errors
