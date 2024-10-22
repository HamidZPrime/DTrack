from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser
from qr_generator.models import CertificateQR
from approval.models import ApprovalStatus
from django.utils import timezone
import hashlib
import re
import PyPDF2
import pytesseract
from PIL import Image


class Certificate(models.Model):
    """
    Model to store and manage uploaded certificates securely with tamper detection and versioning.
    Each certificate is linked to a supplier and a unique QR code for verification.
    """
    supplier = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'supplier'},
                                 verbose_name=_("Supplier"))
    name = models.CharField(_("Certificate Name"), max_length=255)
    file = models.FileField(_("Certificate File"), upload_to='certificates/')
    file_hash = models.CharField(_("File Hash"), max_length=64, editable=False, blank=True)
    description = models.TextField(_("Description"), blank=True)
    upload_time = models.DateTimeField(_("Upload Time"), auto_now_add=True)
    last_checked = models.DateTimeField(_("Last Checked"), null=True, blank=True)
    issue_date = models.DateField(_("Issue Date"), null=True, blank=True)
    expiry_date = models.DateField(_("Expiry Date"), null=True, blank=True)
    verified = models.BooleanField(_("Verified"), default=False)
    version = models.PositiveIntegerField(_("Version"), default=1)
    previous_versions = models.JSONField(_("Previous Versions"), null=True, blank=True)
    approved = models.BooleanField(_("Approved"), default=False)
    approval_status = models.CharField(_("Approval Status"), max_length=10, choices=ApprovalStatus.choices,
                                       default=ApprovalStatus.PENDING)
    suspected_tampered = models.BooleanField(_("Suspected Tampered"), default=False)

    certificate_qr = models.OneToOneField(CertificateQR, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name="certificate", verbose_name=_("Certificate QR Code"))

    class Meta:
        verbose_name = _("Certificate")
        verbose_name_plural = _("Certificates")
        indexes = [
            models.Index(fields=['supplier']),
            models.Index(fields=['file_hash']),
        ]

    def __str__(self):
        return f"{self.name} - {self.supplier.get_full_name()}"

    def calculate_file_hash(self):
        """
        Generate a SHA-256 hash for the uploaded file.
        """
        hash_sha256 = hashlib.sha256()
        if self.file and hasattr(self.file, 'open'):
            with self.file.open('rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        return None

    def extract_text_from_file(self):
        """
        Extract text from the uploaded file using appropriate methods based on file type.
        """
        if self.file:
            file_extension = self.file.name.split('.')[-1].lower()

            if file_extension == 'pdf':
                return self.extract_text_from_pdf()
            elif file_extension in ['jpg', 'jpeg', 'png']:
                return self.extract_text_from_image()

        return ""

    def extract_text_from_pdf(self):
        """
        Extract text from a PDF file using PyPDF2.
        """
        text = ""
        try:
            with self.file.open('rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
        return text

    def extract_text_from_image(self):
        """
        Extract text from an image file using OCR (pytesseract).
        """
        text = ""
        try:
            with self.file.open('rb') as image_file:
                image = Image.open(image_file)
                text = pytesseract.image_to_string(image)
        except Exception as e:
            print(f"Error extracting text from image: {e}")
        return text

    def validate_dates(self):
        """
        Validate the extracted dates from the certificate file to match manually entered dates.
        """
        extracted_text = self.extract_text_from_file()
        if not extracted_text:
            return False

        # Example date patterns (you can adjust based on your certificate format)
        date_pattern = r"\b(\d{4}-\d{2}-\d{2})\b"  # Example: "2024-12-31"

        # Find all dates in the extracted text
        extracted_dates = re.findall(date_pattern, extracted_text)

        # Convert string dates to date objects for comparison
        extracted_dates = [timezone.datetime.strptime(date_str, "%Y-%m-%d").date() for date_str in extracted_dates]

        # Validate manually entered issue and expiry dates
        if self.issue_date in extracted_dates and self.expiry_date in extracted_dates:
            return True

        return False

    def save(self, *args, **kwargs):
        """
        Override save method to validate date consistency, calculate file hash, and manage QR code and approvals.
        """
        # Validate the manually entered dates against extracted dates
        if not self.validate_dates():
            raise ValueError(_("The manually entered dates do not match the dates found in the uploaded certificate file."))

        current_hash = self.calculate_file_hash()

        # Check if the file has been modified or a new certificate is being uploaded
        if self.pk:
            existing_certificate = Certificate.objects.get(pk=self.pk)
            if existing_certificate.file_hash != current_hash:
                # Archive the previous version
                if not self.previous_versions:
                    self.previous_versions = []
                self.previous_versions.append({
                    "version": existing_certificate.version,
                    "file_hash": existing_certificate.file_hash,
                    "upload_time": str(existing_certificate.upload_time),
                })
                self.version += 1

        self.file_hash = current_hash

        # Generate QR Code if approved and not already set
        if not self.certificate_qr and self.approval_status == ApprovalStatus.APPROVED:
            certificate_qr = CertificateQR.objects.create(certificate=self)
            self.certificate_qr = certificate_qr

        if self.approval_status == ApprovalStatus.APPROVED:
            self.approved = True

        super().save(*args, **kwargs)

    def verify_integrity(self):
        """
        Verify the integrity of the uploaded file by comparing the stored hash with the current hash.
        """
        current_hash = self.calculate_file_hash()
        if current_hash and current_hash == self.file_hash:
            self.verified = True
            self.suspected_tampered = False
        else:
            self.verified = False
            self.suspected_tampered = True  # Mark as suspected tampered if verification fails
        self.last_checked = timezone.now()
        self.save()

    def has_file_been_tampered(self):
        """
        Check if the file's current hash matches the stored hash to detect tampering.
        """
        return self.calculate_file_hash() != self.file_hash

    def check_and_log_integrity(self):
        """
        Periodically check and log the integrity of the certificate.
        """
        self.verify_integrity()
        if self.suspected_tampered:
            # Log or notify an admin or auditor in case of tampering detection
            print(f"Suspected tampering detected for certificate: {self.name} by {self.supplier.get_full_name()}")
