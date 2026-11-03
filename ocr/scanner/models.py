from django.db import models


class Scan(models.Model):
    MODE_CHOICES = [("bw", "Black & White"), ("gray", "Grayscale"), ("color", "Color")]
    LANG_CHOICES = [("eng", "English"), ("hin", "Hindi")]

    title = models.CharField(max_length=200, blank=True)
    original = models.ImageField(upload_to="originals/")
    scanned = models.ImageField(upload_to="scanned/", blank=True)
    text = models.TextField(blank=True)
    language = models.CharField(max_length=10, choices=LANG_CHOICES, default="eng")
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default="bw")
    ocr_provider = models.CharField(max_length=30, blank=True)
    ocr_error = models.TextField(blank=True)
    corners_detected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"Scan #{self.pk}"
