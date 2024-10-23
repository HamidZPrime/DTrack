# qr_generator/admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SupplierQR, ProductQR, CertificateQR
from django.utils.html import format_html

@admin.register(SupplierQR)
class SupplierQRAdmin(admin.ModelAdmin):
    list_display = ("supplier", "qr_token", "qr_code_preview", "created_at")
    search_fields = (
        "supplier__email",
        "supplier__first_name",
        "supplier__last_name",
        "qr_token",
    )
    readonly_fields = ("qr_code_image", "qr_token", "qr_code_preview", "created_at")

    def qr_code_preview(self, obj):
        if obj.qr_code_image:
            return format_html(
                '<img src="{}" width="100" height="100" />'.format(obj.qr_code_image.url)
            )
        return _("No QR Code")

    qr_code_preview.short_description = _("QR Code Preview")

@admin.register(ProductQR)
class ProductQRAdmin(admin.ModelAdmin):
    list_display = ("supplier", "product_id", "qr_token", "qr_code_preview", "created_at")
    search_fields = ("supplier__email", "supplier__first_name", "supplier__last_name", "product_id", "qr_token")
    readonly_fields = ("qr_code_image", "qr_token", "qr_code_preview", "created_at")

    def qr_code_preview(self, obj):
        if obj.qr_code_image:
            return format_html(
                '<img src="{}" width="100" height="100" />'.format(obj.qr_code_image.url)
            )
        return _("No QR Code")

    qr_code_preview.short_description = _("QR Code Preview")

@admin.register(CertificateQR)
class CertificateQRAdmin(admin.ModelAdmin):
    list_display = ("supplier", "certificate_id", "qr_token", "qr_code_preview", "created_at")
    search_fields = ("supplier__email", "supplier__first_name", "supplier__last_name", "certificate_id", "qr_token")
    readonly_fields = ("qr_code_image", "qr_token", "qr_code_preview", "created_at")

    def qr_code_preview(self, obj):
        if obj.qr_code_image:
            return format_html(
                '<img src="{}" width="100" height="100" />'.format(obj.qr_code_image.url)
            )
        return _("No QR Code")

    qr_code_preview.short_description = _("QR Code Preview")
