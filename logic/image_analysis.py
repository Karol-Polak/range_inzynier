import cv2
import numpy as np
import pytesseract


def detect_numbers(image):
    """
    Wykrywa cyfry na tarczy i tworzy rozszerzoną maskę do ignorowania tych obszarów.

    Args:
        image: Obraz wejściowy (numpy array)

    Returns:
        mask: Obraz binarny z maską cyfr
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Adaptacyjna binaryzacja dla lepszego wykrywania cyfr
    adaptive_thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 51, 10
    )

    # Wykrycie cyfr za pomocą Tesseract OCR
    mask = np.zeros_like(gray, dtype=np.uint8)
    boxes = pytesseract.image_to_boxes(gray, config="--psm 6 digits")

    h, w = gray.shape
    for b in boxes.splitlines():
        b = b.split()
        x, y, x2, y2 = int(b[1]), h - int(b[2]), int(b[3]), h - int(b[4])
        cv2.rectangle(mask, (x, y), (x2, y2), 255, -1)

    # Powiększenie maski
    kernel = np.ones((15, 15), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=2)

    print("[INFO] Maska cyfr utworzona.")
    return mask


def filter_hits_by_shape_and_texture(image, circles, text_mask):
    """
    Filtruje wykryte trafienia, aby odrzucić fałszywe trafienia na cyfrach.

    Args:
        image: Obraz wejściowy (numpy array)
        circles: Lista wykrytych trafień [(x, y, r), ...]
        text_mask: Maska cyfr

    Returns:
        filtered_circles: Lista prawdziwych trafień
    """
    filtered_circles = []
    rejected_by_text = 0
    rejected_by_shape = 0
    rejected_by_texture = 0

    for (x, y, r) in circles:
        # Jeśli środek wykrytej przestrzeliny znajduje się w masce cyfr, odrzucamy ją
        if text_mask[y, x] != 0:
            rejected_by_text += 1
            continue

        # Pobieramy ROI wokół przestrzeliny
        roi = image[max(0, y - r):min(y + r, image.shape[0]), max(0, x - r):min(x + r, image.shape[1])]

        # Analiza kształtu - sprawdzamy stosunek szerokości do wysokości
        contours, _ = cv2.findContours(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY), cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            x_, y_, w_, h_ = cv2.boundingRect(c)
            aspect_ratio = w_ / float(h_)

            if aspect_ratio < 0.7 or aspect_ratio > 1.3:
                rejected_by_shape += 1
                continue

        # Analiza tekstury – przestrzeliny mają nieregularne krawędzie, cyfry są jednolite
        std_dev = np.std(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY))
        if std_dev < 15:
            rejected_by_texture += 1
            continue

        filtered_circles.append((x, y, r))

    print(
        f"[INFO] Odrzucone trafienia: {rejected_by_text} (tekst), {rejected_by_shape} (kształt), {rejected_by_texture} (tekstura)")
    print(f"[INFO] Łącznie zaakceptowanych trafień: {len(filtered_circles)}")

    return filtered_circles


def detect_hits_with_text_filter(image_path):
    """
    Wykrywa przestrzeliny na obrazie, eliminując błędne wykrycia na cyfrach.

    Args:
        image_path (str): Ścieżka do obrazu

    Returns:
        list: Lista krotek (x, y, r) dla wykrytych trafień
    """
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Nie można wczytać obrazu: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    print("[INFO] Rozpoczynam wykrywanie cyfr...")
    text_mask = detect_numbers(image)

    print("[INFO] Rozpoczynam wykrywanie przestrzelin...")
    detected_circles = cv2.HoughCircles(
        gray_blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.0,
        minDist=15,
        param1=50,
        param2=25,
        minRadius=5,
        maxRadius=50
    )

    circles = []
    if detected_circles is not None:
        detected_circles = np.uint16(np.around(detected_circles))
        for x, y, r in detected_circles[0, :]:
            circles.append((x, y, r))

    print(f"[INFO] Wykryto {len(circles)} trafień przed filtracją.")

    filtered_circles = filter_hits_by_shape_and_texture(image, circles, text_mask)

    print(f"[INFO] Wykryte końcowe trafienia: {len(filtered_circles)}")

    return filtered_circles
