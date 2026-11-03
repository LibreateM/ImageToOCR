# ImageToOCR

A Django-based web application that turns photos of documents, receipts, notes, and screenshots into clean, searchable text using computer vision and OCR.

ImageToOCR automatically:
- uploads an image
- detects the document boundaries
- corrects perspective and enhances the scan
- extracts text using OCR.space with a local Tesseract fallback
- stores the original image, processed image, OCR result, and history

## Features

- Upload images in JPG/PNG format
- Automatic document boundary detection with OpenCV
- Perspective correction and scan enhancement
- Multiple processing modes: Black & White, Grayscale, and Color
- OCR in English and Hindi
- View extraction history and download recognized text
- Simple Django admin + template-based UI

## Tech Stack

- Python
- Django 6
- OpenCV
- Pillow
- NumPy
- OCR.space API
- Tesseract OCR (fallback)

## Project Structure

```text
ImageToOCR/
├── README.md
├── ocr/
│   ├── db.sqlite3
│   ├── manage.py
│   ├── requirements.txt
│   ├── media/
│   ├── ocr/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── scanner/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── ocr_engine.py
│   │   ├── scanner_cv.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── templates/
│       └── scanner/
│           ├── base.html
│           ├── detail.html
│           ├── history.html
│           └── upload.html
└── .gitignore
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/LibreateM/ImageToOCR.git
cd ImageToOCR
```

### 2. Create a virtual environment

```bash
cd ocr
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Start the server

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## OCR Configuration

The app uses the OCR.space API by default.

Update the API key in:

```python
ocr/ocr/settings.py
```

```python
OCR_SPACE_API_KEY = "YOUR_API_KEY_HERE"
```

If OCR.space fails or the key is unavailable, the app will try a local Tesseract fallback.

### Tesseract install (optional fallback)

- macOS:
  ```bash
  brew install tesseract
  ```
- Ubuntu/Debian:
  ```bash
  sudo apt-get install tesseract-ocr
  ```
- Windows:
  Download and install Tesseract from the official project site and ensure it is available on PATH.

## How It Works

1. User uploads an image.
2. The app reads the file and corrects EXIF orientation.
3. OpenCV detects the document boundaries and performs preprocessing.
4. A cleaned scan is generated.
5. OCR is run using OCR.space.
6. If the cloud OCR fails, Tesseract is used as a fallback.
7. The result is saved and displayed in the app history.

## Usage

- Visit the upload page.
- Choose the image file.
- Select language (English/Hindi) and processing mode.
- Submit the form.
- Review the extracted text and saved scan.
- Download the result as a `.txt` file if needed.

## Notes

This project is a practical OCR demo and is suitable for local development and experimentation. For production use, you would typically add:

- environment-based secret management
- proper deployment configuration
- logging and monitoring
- authentication and authorization
- stronger input validation and security hardening

## License

This project does not currently include a license file. Add one if you plan to distribute or share it publicly.

## Contributing

Contributions are welcome. You can:

- improve OCR accuracy
- add better document preprocessing
- support more languages
- improve the UI
- refactor the codebase for production readiness

## Contact

For questions or collaboration, use the repository's GitHub issue tracker or contact the project maintainer.
