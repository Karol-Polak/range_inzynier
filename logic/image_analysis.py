import cv2
import numpy as np


def detect_hits(image_path, debug=False, save_debug=False):
    """
    Wykrywa trafienia na tarczy z uwzględnieniem ciemnych obszarów na jasnym tle.
    """
    # Wczytanie obrazu
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Nie można wczytać obrazu: {image_path}")

    # Konwersja do przestrzeni HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Progowanie – wykrywanie ciemnych obszarów
    lower_dark = np.array([0, 0, 0])  # Ciemne obszary
    upper_dark = np.array([180, 255, 100])  # Górny próg dla ciemnych obszarów
    mask = cv2.inRange(hsv, lower_dark, upper_dark)

    # Operacje morfologiczne – usunięcie szumów i wypełnienie luk
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask_closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask_opened = cv2.morphologyEx(mask_closed, cv2.MORPH_OPEN, kernel, iterations=2)

    # Transformacja odległości – wykrycie rdzeni trafień
    dist_transform = cv2.distanceTransform(mask_opened, cv2.DIST_L2, 5)
    ret, sure_fg = cv2.threshold(dist_transform, 0.4 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)

    # Wyznaczenie tła przez dylatację maski
    sure_bg = cv2.dilate(mask_opened, kernel, iterations=3)
    unknown = cv2.subtract(sure_bg, sure_fg)

    # Markerowanie – każdy wyraźny obszar trafienia otrzymuje unikalny marker
    ret, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    # Zastosowanie algorytmu watershed
    image_ws = image.copy()
    markers = cv2.watershed(image_ws, markers)

    detected_hits = []
    for marker in range(2, markers.max() + 1):
        # Tworzymy maskę dla danego regionu
        hit_mask = np.uint8(markers == marker)
        area = cv2.countNonZero(hit_mask)
        if area < 20 or area > 2000:  # Filtrowanie szumów
            continue

        # Obliczamy centroid regionu
        M = cv2.moments(hit_mask)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            detected_hits.append((cx, cy))

    # Opcje debugowania
    if debug or save_debug:
        debug_image = image.copy()
        for (x, y) in detected_hits:
            cv2.circle(debug_image, (x, y), 10, (0, 0, 255), -1)

        if debug:
            cv2.imshow("Detected Hits", debug_image)
            cv2.imshow("Mask Opened", mask_opened)
            cv2.imshow("Distance Transform", cv2.normalize(dist_transform, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        if save_debug:
            cv2.imwrite("debug_hits.png", debug_image)

    return detected_hits


