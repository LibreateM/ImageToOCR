"""Step 2: OCR.space cloud API + local Tesseract fallback."""
import cv2
import requests
from django.conf import settings

OCR_URL = "https://api.ocr.space/parse/image"


class OCRError(Exception):
    pass


def compress_for_ocr(img, max_width=1600, max_bytes=1_000_000):
    """Free tier ki size limit ke andar JPEG banao (resize + quality kam)."""
    h, w = img.shape[:2]
    if w > max_width:
        img = cv2.resize(img, (max_width, int(h * max_width / w)), interpolation=cv2.INTER_AREA)
    quality = 85
    while True:
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not ok:
            raise OCRError("Image encode nahi hui")
        if len(buf) <= max_bytes:
            return buf.tobytes()
        if quality > 45:
            quality -= 10
        else:  # quality already low, ab size chhoti karo
            img = cv2.resize(img, None, fx=0.8, fy=0.8, interpolation=cv2.INTER_AREA)


def ocr_space(image_bytes, language="eng", engine=2, timeout=60):
    key = settings.OCR_SPACE_API_KEY
    if not key:
        raise OCRError("OCR_SPACE_API_KEY set nahi hai (.env check karo)")
    try:
        resp = requests.post(
            OCR_URL,
            files={"file": ("scan.jpg", image_bytes, "image/jpeg")},
            data={
                "apikey": key,
                "language": language,
                "OCREngine": engine,
                "scale": "true",
                "detectOrientation": "true",
                "isOverlayRequired": "false",
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise OCRError(f"OCR.space request fail: {exc}") from exc

    if data.get("IsErroredOnProcessing"):
        msg = data.get("ErrorMessage") or "Unknown OCR.space error"
        if isinstance(msg, list):
            msg = "; ".join(msg)
        raise OCRError(msg)

    results = data.get("ParsedResults") or []
    return "\n".join(r.get("ParsedText", "") for r in results).strip()


def tesseract_fallback(img, language="eng"):
    """Cloud fail ho toh local Tesseract (binary install hona chahiye)."""
    try:
        import pytesseract
    except ImportError as exc:
        raise OCRError("pytesseract installed nahi hai") from exc
    lang = "hin+eng" if language == "hin" else "eng"
    try:
        return pytesseract.image_to_string(img, lang=lang).strip()
    except Exception as exc:  # TesseractNotFoundError etc.
        raise OCRError(f"Tesseract fail: {exc}") from exc


def run_ocr(scanned_img, language="eng"):
    """Returns (text, provider, error_message)."""
    # Note: Hindi ke liye Engine 1 use ho raha hai; supported languages OCR.space docs mein verify karo.
    engine = 1 if language == "hin" else 2
    try:
        payload = compress_for_ocr(scanned_img)
        return ocr_space(payload, language=language, engine=engine), f"ocr.space-e{engine}", ""
    except OCRError as cloud_err:
        try:
            return tesseract_fallback(scanned_img, language), "tesseract", f"Cloud OCR fail ({cloud_err}); Tesseract use hua."
        except OCRError as local_err:
            return "", "", f"Cloud: {cloud_err} | Local: {local_err}"
