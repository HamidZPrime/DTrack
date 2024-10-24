from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser
from approval.models import ApprovalStatus
import qrcode
from io import BytesIO
from django.core.files import File
from django.urls import reverse
from django.conf import settings
import uuid
import os


class SupplierQR(models.Model):
    """
    Model to generate and store QR codes for suppliers.
    Each supplier is associated with a unique QR code, and the code points to a secure URL.
    """
    supplier = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "supplier"},
        verbose_name=_("Supplier"),
    )
    qr_code_image = models.ImageField(
        _("QR Code Image"), upload_to="qr_codes/suppliers/", blank=True
    )
    qr_token = models.UUIDField(
        _("QR Token"), default=uuid.uuid4, editable=False, unique=True
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def generate_qr_code(self, force_recreate=False):
        """Generates a QR code for the supplier's secure URL if approved."""
        if self.supplier.approval_status == ApprovalStatus.APPROVED and (force_recreate or not self.qr_code_image):
            base_url = settings.SITE_URL
            qr_content = f"{base_url}{reverse('supplier_detail', args=[self.qr_token])}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)

            img = qr.make_image(fill_color='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            file_name = f"supplier_{self.supplier.id}_qr.png"
            self.qr_code_image.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code_image or not os.path.isfile(self.qr_code_image.path):
            self.generate_qr_code(force_recreate=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR Code for {self.supplier.get_full_name()}"


class ProductQR(models.Model):
    """
    Model to generate and store QR codes for each product.
    Each product added by a supplier is associated with its unique QR code, pointing to a secure URL.
    """
    supplier = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "supplier"},
        verbose_name=_("Supplier"),
    )
    product_id = models.CharField(_("Product ID"), max_length=100)
    qr_code_image = models.ImageField(
        _("QR Code Image"), upload_to="qr_codes/products/", blank=True
    )
    qr_token = models.UUIDField(
        _("QR Token"), default=uuid.uuid4, editable=False, unique=True
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def generate_qr_code(self, force_recreate=False):
        """Generates a QR code for the product's secure URL if the supplier is approved."""
        if self.supplier.approval_status == ApprovalStatus.APPROVED and (force_recreate or not self.qr_code_image):
            base_url = settings.SITE_URL
            qr_content = f"{base_url}{reverse('product_detail', args=[self.qr_token])}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)

            img = qr.make_image(fill_color='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            file_name = f"product_{self.product_id}_qr.png"
            self.qr_code_image.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code_image or not os.path.isfile(self.qr_code_image.path):
            self.generate_qr_code(force_recreate=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR Code for Product {self.product_id}"


class CertificateQR(models.Model):
    """
    Model to generate and store QR codes for each certificate.
    Each certificate is associated with its unique QR code for validation, pointing to a secure URL.
    """
    supplier = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "supplier"},
        verbose_name=_("Supplier"),
    )
    certificate_id = models.CharField(_("Certificate ID"), max_length=100)
    qr_code_image = models.ImageField(
        _("QR Code Image"), upload_to="qr_codes/certificates/", blank=True
    )
    qr_token = models.UUIDField(
        _("QR Token"), default=uuid.uuid4, editable=False, unique=True
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def generate_qr_code(self, force_recreate=False):
        """Generates a QR code for the certificate's secure URL if the supplier is approved."""
        if self.supplier.approval_status == ApprovalStatus.APPROVED and (force_recreate or not self.qr_code_image):
            base_url = settings.SITE_URL
            qr_content = f"{base_url}{reverse('certificate_detail', args=[self.qr_token])}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)

            img = qr.make_image(fill_color='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            file_name = f"certificate_{self.certificate_id}_qr.png"
            self.qr_code_image.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code_image or not os.path.isfile(self.qr_code_image.path):
            self.generate_qr_code(force_recreate=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR Code for Certificate {self.certificate_id}"
