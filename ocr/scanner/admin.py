from django.contrib import admin

from .models import Scan


@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    list_display = ("__str__", "language", "ocr_provider", "corners_detected", "created_at")
    search_fields = ("title", "text")
