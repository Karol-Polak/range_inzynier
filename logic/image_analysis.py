import cv2
import numpy as np

def detect_hits(image_path, debug=False):
    """
    Analizuje obraz tarczy i wykrywa trafienia łącząc segmentację maski HSV
    i transformację Hougha. Zwraca listę współrzędnych [(x, y)] wykrytych trafień.

    :param image_path: Ścieżka do obrazu tarczy.
    :param debug: Jeśli True, wyświetli obrazy pośrednie dla podglądu.
    :return: Lista wykrytych trafień [(x, y)].
    """
    # Wczytanie obrazu i konwersja do HSV
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Nie można wczytać obrazu: {image_path}")

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Definicja zakresu dla jasnych obszarów (np. białych punktów)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 80, 255])
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Operacje morfologiczne w celu usunięcia szumów
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Transformacja Hougha do wykrywania okręgów na masce
    circles = cv2.HoughCircles(
        mask,  # Maskowany obraz
        cv2.HOUGH_GRADIENT,  # Metoda transformacji
        dp=1.5,  # Rozdzielczość akumulatora w stosunku do obrazu
        minDist=15,  # Minimalna odległość między środkami okręgów
        param1=50,  # Górny próg dla detekcji krawędzi Canny
        param2=15,  # Próg akumulatora (niższa wartość oznacza więcej wykryć)
        minRadius=5,  # Minimalny promień okręgu
        maxRadius=30  # Maksymalny promień okręgu
    )

    detected_hits = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            x, y, r = circle
            detected_hits.append((x, y))

    # Debugowanie: Wyświetlenie wyników
    if debug:
        debug_image = image.copy()
        for (x, y) in detected_hits:
            cv2.circle(debug_image, (x, y), 5, (0, 0, 255), -1)  # Czerwone punkty
        cv2.imshow("Detected Hits", debug_image)
        cv2.imshow("Mask", mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return detected_hits
