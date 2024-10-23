from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Certificate
from qr_generator.models import CertificateQR
from django.utils.html import format_html


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """
    Admin interface to manage Certificates.
    Includes viewing the QR code details and handling all certificate management tasks.
    """

    list_display = (
        "name",
        "supplier",
        "issue_date",
        "expiry_date",
        "approved",
        "get_qr_code_image",
        "suspected_tampered",
        "upload_time",
    )
    list_filter = ("approved", "suspected_tampered", "upload_time", "expiry_date")
    search_fields = (
        "name",
        "supplier__email",
        "supplier__first_name",
        "supplier__last_name",
    )
    readonly_fields = (
        "get_qr_code_image",
        "file_hash",
        "upload_time",
        "version",
        "previous_versions",
        "last_checked",
        "certificate_qr",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "supplier",
                    "name",
                    "description",
                    "file",
                    "get_qr_code_image",
                )
            },
        ),
        (
            _("Dates & Versions"),
            {
                "fields": (
                    "issue_date",
                    "expiry_date",
                    "upload_time",
                    "last_checked",
                    "version",
                    "previous_versions",
                )
            },
        ),
        (
            _("Verification & Integrity"),
            {
                "fields": (
                    "file_hash",
                    "verified",
                    "suspected_tampered",
                    "approval_status",
                    "approved",
                    "certificate_qr",
                )
            },
        ),
    )

    def get_qr_code_image(self, obj):
        """
        Display the QR code image for the certificate.
        """
        if obj.certificate_qr and obj.certificate_qr.qr_code_image:
            return format_html(
                f'<img src="{obj.certificate_qr.qr_code_image.url}" width="100" height="100" />'
            )
        return _("No QR Code")

    get_qr_code_image.short_description = _("QR Code Image")

    def save_model(self, request, obj, form, change):
        """
        Override the save method to update QR code generation based on changes.
        """
        # Generate or update QR code only if the certificate is approved
        if obj.approval_status == ApprovalStatus.APPROVED and not obj.certificate_qr:
            certificate_qr = CertificateQR.objects.create(
                supplier=obj.supplier, certificate_id=obj.pk
            )
            obj.certificate_qr = certificate_qr
            obj.certificate_qr.generate_qr_code()

        super().save_model(request, obj, form, change)
