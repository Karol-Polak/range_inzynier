import cv2
import numpy as np

def detect_hits(image_path):
    """
    Analizuje obraz tarczy i wykrywa trafienia jako ciemne okręgi.
    Zwraca listę współrzędnych [(x, y)] wykrytych trafień.
    """
    # Wczytanie obrazu w skali szarości
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return []

    # Rozmycie obrazu w celu usunięcia szumów
    blurred = cv2.GaussianBlur(image, (9, 9), 2)

    # Wykrywanie okręgów (potencjalnych trafień)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                               param1=50, param2=30, minRadius=5, maxRadius=30)

    detected_hits = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for circle in circles[0, :]:
            x, y, r = circle
            detected_hits.append((x, y))

    return detected_hits
