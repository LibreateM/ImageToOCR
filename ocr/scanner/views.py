import uuid

import cv2
import numpy as np
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from PIL import Image, ImageOps

from .forms import UploadForm
from .models import Scan
from .ocr_engine import run_ocr
from .scanner_cv import scan_document


def upload(request):
    form = UploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        f = form.cleaned_data["image"]
        language = form.cleaned_data["language"]
        mode = form.cleaned_data["mode"]

        # EXIF rotation fix (phone photos), phir OpenCV BGR array
        pil = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

        scanned, detected = scan_document(img, mode)
        ok, buf = cv2.imencode(".jpg", scanned, [cv2.IMWRITE_JPEG_QUALITY, 90])

        scan = Scan(
            title=f.name.rsplit(".", 1)[0][:200],
            language=language,
            mode=mode,
            corners_detected=detected,
        )
        f.seek(0)
        scan.original.save(f.name, f, save=False)
        scan.scanned.save(f"scan_{uuid.uuid4().hex[:10]}.jpg", ContentFile(buf.tobytes()), save=False)

        text, provider, error = run_ocr(scanned, language)
        scan.text, scan.ocr_provider, scan.ocr_error = text, provider, error
        scan.save()

        if error:
            messages.warning(request, error)
        if not detected:
            messages.info(request, "Document ke 4 corners auto-detect nahi hue, poori image use hui.")
        return redirect("detail", pk=scan.pk)

    return render(request, "scanner/upload.html", {"form": form})


def detail(request, pk):
    return render(request, "scanner/detail.html", {"scan": get_object_or_404(Scan, pk=pk)})


def history(request):
    q = request.GET.get("q", "").strip()
    scans = Scan.objects.all()
    if q:
        scans = scans.filter(Q(text__icontains=q) | Q(title__icontains=q))
    return render(request, "scanner/history.html", {"scans": scans, "q": q})


def download_text(request, pk):
    scan = get_object_or_404(Scan, pk=pk)
    resp = HttpResponse(scan.text, content_type="text/plain; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="scan_{scan.pk}.txt"'
    return resp


@require_POST
def delete(request, pk):
    scan = get_object_or_404(Scan, pk=pk)
    scan.original.delete(save=False)
    scan.scanned.delete(save=False)
    scan.delete()
    messages.success(request, "Scan delete ho gaya.")
    return redirect("history")
