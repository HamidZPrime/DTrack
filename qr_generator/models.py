# qr_generator/models.py

from django.db import models
from django.utils.translation import (
    gettext_lazy as _,
)  # Import gettext_lazy for translation
from accounts.models import CustomUser
from approval.models import ApprovalStatus  # Import approval status choices
import qrcode
from io import BytesIO
from django.core.files import File
import uuid


class SupplierQR(models.Model):
    """
    Model to generate and store QR codes for suppliers.
    Each supplier is associated with a unique QR code, and the code points to an encrypted or tokenized URL.
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

    def generate_qr_code(self):
        """Generates a QR code for the supplier's encrypted or tokenized URL if approved."""
        if self.supplier.approval_status == ApprovalStatus.APPROVED:
            qr_content = (
                f"/supplier/{self.qr_token}/"  # Use a tokenized URL for security
            )
            qr = qrcode.make(qr_content)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            file_name = f"supplier_{self.supplier.id}_qr.png"
            self.qr_code_image.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code_image:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR Code for {self.supplier.get_full_name()}"


class ProductQR(models.Model):
    """
    Model to generate and store QR codes for each product.
    Each product added by a supplier is associated with its unique QR code, pointing to an encrypted or tokenized URL.
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

    def generate_qr_code(self):
        """Generates a QR code for the product's encrypted or tokenized URL if the supplier is approved."""
        if self.supplier.approval_status == ApprovalStatus.APPROVED:
            qr_content = (
                f"/product/{self.qr_token}/"  # Use a tokenized URL for security
            )
            qr = qrcode.make(qr_content)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            file_name = f"product_{self.product_id}_qr.png"
            self.qr_code_image.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code_image:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR Code for Product {self.product_id}"


class CertificateQR(models.Model):
    """
    Model to generate and store QR codes for each certificate.
    Each certificate is associated with its unique QR code for validation, pointing to an encrypted or tokenized URL.
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

    def generate_qr_code(self):
        """Generates a QR code for the certificate's encrypted or tokenized URL if the supplier and certificate are approved."""
        if self.supplier.approval_status == ApprovalStatus.APPROVED:
            qr_content = (
                f"/certificate/{self.qr_token}/"  # Use a tokenized URL for security
            )
            qr = qrcode.make(qr_content)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            file_name = f"certificate_{self.certificate_id}_qr.png"
            self.qr_code_image.save(file_name, File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code_image:
            self.generate_qr_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR Code for Certificate {self.certificate_id}"
