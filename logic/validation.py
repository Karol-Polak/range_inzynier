def validate_training_data(distance, shots, image_path):
    """Waliduje dane treningowe."""
    errors = []

    # Walidacja dystansu
    try:
        distance_int = int(distance)
        if distance_int <= 0 or distance_int > 1000:
            errors.append("Dystans musi być liczbą z zakresu 1-1000.")
    except ValueError:
        errors.append("Dystans musi być liczbą całkowitą.")

    # Walidacja liczby strzałów
    try:
        shots_int = int(shots)
        if shots_int <= 0 or shots_int > 100:
            errors.append("Liczba strzałów musi być liczbą z zakresu 1-100.")
    except ValueError:
        errors.append("Liczba strzałów musi być liczbą całkowitą.")

    # Walidacja obecności obrazu
    if not image_path:
        errors.append("Musisz wczytać zdjęcie tarczy.")

    return errors
