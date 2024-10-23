from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SupplierQR, ProductQR, CertificateQR
from django.utils.html import format_html

@admin.register(SupplierQR)
class SupplierQRAdmin(admin.ModelAdmin):
    """
    Admin interface to manage Supplier QR codes.
    Includes visualization of the QR code and details of the associated supplier.
    """
    list_display = ('supplier', 'qr_token', 'get_qr_code_image', 'created_at')
    search_fields = ('supplier__email', 'supplier__first_name', 'supplier__last_name', 'qr_token')
<<<<<<< HEAD
    readonly_fields = ('qr_code_image', 'qr_token', 'get_qr_code_image', 'created_at')
=======
    readonly_fields = ('qr_token', 'get_qr_code_image', 'created_at')
>>>>>>> fbe776ad210208b47bf216e2553c92919cdbdad8

    def get_qr_code_image(self, obj):
        """
        Display the QR code image.
        """
        if obj.qr_code_image:
            return format_html(f'<img src="{obj.qr_code_image.url}" width="100" height="100" />')
        return _("No QR Code")
    get_qr_code_image.short_description = _("QR Code Image")

<<<<<<< HEAD
    def save_model(self, request, obj, form, change):
        """
        Override save_model to automatically generate QR code image upon save.
        """
        obj.generate_qr_code()
        super().save_model(request, obj, form, change)

=======
>>>>>>> fbe776ad210208b47bf216e2553c92919cdbdad8

@admin.register(ProductQR)
class ProductQRAdmin(admin.ModelAdmin):
    """
    Admin interface to manage Product QR codes.
    Includes visualization of the QR code and details of the associated supplier and product.
    """
    list_display = ('supplier', 'product_id', 'qr_token', 'get_qr_code_image', 'created_at')
    search_fields = ('supplier__email', 'supplier__first_name', 'supplier__last_name', 'product_id', 'qr_token')
<<<<<<< HEAD
    readonly_fields = ('qr_code_image', 'qr_token', 'get_qr_code_image', 'created_at')
=======
    readonly_fields = ('qr_token', 'get_qr_code_image', 'created_at')
>>>>>>> fbe776ad210208b47bf216e2553c92919cdbdad8

    def get_qr_code_image(self, obj):
        """
        Display the QR code image.
        """
        if obj.qr_code_image:
            return format_html(f'<img src="{obj.qr_code_image.url}" width="100" height="100" />')
        return _("No QR Code")
    get_qr_code_image.short_description = _("QR Code Image")

<<<<<<< HEAD
    def save_model(self, request, obj, form, change):
        """
        Override save_model to automatically generate QR code image upon save.
        """
        obj.generate_qr_code()
        super().save_model(request, obj, form, change)

=======
>>>>>>> fbe776ad210208b47bf216e2553c92919cdbdad8

@admin.register(CertificateQR)
class CertificateQRAdmin(admin.ModelAdmin):
    """
    Admin interface to manage Certificate QR codes.
    Includes visualization of the QR code and details of the associated supplier and certificate.
    """
    list_display = ('supplier', 'certificate_id', 'qr_token', 'get_qr_code_image', 'created_at')
    search_fields = ('supplier__email', 'supplier__first_name', 'supplier__last_name', 'certificate_id', 'qr_token')
<<<<<<< HEAD
    readonly_fields = ('qr_code_image', 'qr_token', 'get_qr_code_image', 'created_at')
=======
    readonly_fields = ('qr_token', 'get_qr_code_image', 'created_at')
>>>>>>> fbe776ad210208b47bf216e2553c92919cdbdad8

    def get_qr_code_image(self, obj):
        """
        Display the QR code image.
        """
        if obj.qr_code_image:
            return format_html(f'<img src="{obj.qr_code_image.url}" width="100" height="100" />')
        return _("No QR Code")
    get_qr_code_image.short_description = _("QR Code Image")
<<<<<<< HEAD

    def save_model(self, request, obj, form, change):
        """
        Override save_model to automatically generate QR code image upon save.
        """
        obj.generate_qr_code()
        super().save_model(request, obj, form, change)

=======
>>>>>>> fbe776ad210208b47bf216e2553c92919cdbdad8
