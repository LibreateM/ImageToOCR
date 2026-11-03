"""Step 1: OpenCV document scanner. Django ke bina bhi chalta hai."""
import cv2
import numpy as np


def order_points(pts):
    """4 points ko [top-left, top-right, bottom-right, bottom-left] order mein lagao."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]   # top-left: smallest x+y
    rect[2] = pts[np.argmax(s)]   # bottom-right: largest x+y
    d = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(d)]   # top-right: smallest y-x
    rect[3] = pts[np.argmax(d)]   # bottom-left: largest y-x
    return rect


def four_point_transform(image, pts):
    """Perspective correction: tilted document ko seedha rectangle bana do."""
    rect = order_points(pts)
    tl, tr, br, bl = rect
    width = int(max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl)))
    height = int(max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl)))
    dst = np.array(
        [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
        dtype="float32",
    )
    matrix = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, matrix, (width, height))


def find_document_contour(image):
    """Image mein sabse bada 4-corner contour dhoondo. Na mile toh None."""
    ratio = image.shape[0] / 500.0
    small = cv2.resize(image, (int(image.shape[1] / ratio), 500))
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(gray, 50, 150)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    min_area = 0.2 * small.shape[0] * small.shape[1]

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(approx) > min_area:
            return approx.reshape(4, 2).astype("float32") * ratio
    return None


def enhance(image, mode="bw"):
    """mode: bw (photocopy look) | gray (CLAHE) | color (as is)."""
    if mode == "color":
        return image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if mode == "gray":
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )


def scan_document(image, mode="bw", corners=None):
    """Returns (scanned_image, corners_detected).
    corners: optional manual 4 points (future: user drag karke de)."""
    pts = corners if corners is not None else find_document_contour(image)
    detected = pts is not None
    warped = four_point_transform(image, pts) if detected else image
    return enhance(warped, mode), detected
