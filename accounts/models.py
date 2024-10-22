from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
import uuid


class CustomUserManager(BaseUserManager):
    """
    Custom manager for handling the creation of different user roles.
    Includes helper methods to create standard users and superusers.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model to support various roles, language preferences, and a one-to-one link with a Supplier QR code for suppliers.
    """
    ROLE_CHOICES = (
        ('admin', _("Admin")),
        ('operator', _("Operator")),
        ('supplier', _("Supplier")),
        ('enduser', _("End User")),
    )

    APPROVAL_CHOICES = (
        ('pending', _("Pending")),
        ('approved', _("Approved")),
        ('rejected', _("Rejected")),
    )

    email = models.EmailField(_("Email Address"), unique=True, max_length=255, db_index=True)
    role = models.CharField(_("Role"), max_length=50, choices=ROLE_CHOICES, default='enduser')
    first_name = models.CharField(_("First Name"), max_length=50, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=50, blank=True)
    phone_number = models.CharField(_("Phone Number"), max_length=15, blank=True)
    is_active = models.BooleanField(_("Active"), default=False)  # User inactive until email verification
    is_staff = models.BooleanField(_("Staff Status"), default=False)
    is_superuser = models.BooleanField(_("Superuser Status"), default=False)
    language = models.CharField(_("Language"), max_length=5, default='en', choices=[('en', 'English'), ('ar', 'Arabic')])
    date_joined = models.DateTimeField(_("Date Joined"), default=timezone.now)
    last_login = models.DateTimeField(_("Last Login"), auto_now=True)

    email_verified = models.BooleanField(_("Email Verified"), default=False)
    profile_complete = models.BooleanField(_("Profile Complete"), default=False)
    is_approved = models.BooleanField(_("Approved"), default=False)
    approval_status = models.CharField(_("Approval Status"), max_length=10, choices=APPROVAL_CHOICES, default='pending')

    supplier_qr = models.OneToOneField(
        'qr_generator.SupplierQR',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplier_user",
        verbose_name=_("Supplier QR Code")
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def generate_supplier_qr(self):
        """Method to create a QR code for a supplier upon registration."""
        if self.role == 'supplier' and not self.supplier_qr and self.is_approved:
            from qr_generator.models import SupplierQR  # Import locally to avoid circular import
            supplier_qr = SupplierQR.objects.create(supplier=self)
            self.supplier_qr = supplier_qr
            self.save()

    def save(self, *args, **kwargs):
        """Override save method to manage email verification, profile, and approval."""
        self.check_certificate_expiration()
        if self.role == 'supplier' and self.approval_status == 'approved':
            self.is_approved = True
            self.generate_supplier_qr()
        super().save(*args, **kwargs)

    def check_certificate_expiration(self):
        """
        Disable user account if they have expired certificates.
        """
        expired_certificates = self.certificate_set.filter(
            expiry_date__lt=timezone.now().date(),
            approved=True
        ).exists()

        if expired_certificates:
            self.is_active = False
        else:
            self.is_active = True


class OperatorPermission(models.Model):
    """Permissions model to assign specific capabilities to operators."""
    operator = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'operator'}, verbose_name=_("Operator"))
    can_manage_users = models.BooleanField(_("Can Manage Users"), default=False)
    can_manage_certificates = models.BooleanField(_("Can Manage Certificates"), default=False)
    can_manage_products = models.BooleanField(_("Can Manage Products"), default=False)
    can_manage_reports = models.BooleanField(_("Can Manage Reports"), default=False)
    can_manage_notifications = models.BooleanField(_("Can Manage Notifications"), default=False)
    can_access_financials = models.BooleanField(_("Can Access Financials"), default=False)
    can_manage_orders = models.BooleanField(_("Can Manage Orders"), default=False)

    class Meta:
        verbose_name = _("Operator Permission")
        verbose_name_plural = _("Operator Permissions")

    def __str__(self):
        return f"Permissions for {self.operator.get_full_name()}"


class PredefinedAdminRight(models.Model):
    """Model to define predefined admin rights for easier permission assignment."""
    name = models.CharField(_("Name"), max_length=50, unique=True)
    description = models.TextField(_("Description"), blank=True)
    can_manage_users = models.BooleanField(_("Can Manage Users"), default=False)
    can_manage_certificates = models.BooleanField(_("Can Manage Certificates"), default=False)
    can_manage_products = models.BooleanField(_("Can Manage Products"), default=False)
    can_manage_reports = models.BooleanField(_("Can Manage Reports"), default=False)
    can_manage_notifications = models.BooleanField(_("Can Manage Notifications"), default=False)
    can_access_financials = models.BooleanField(_("Can Access Financials"), default=False)
    can_manage_orders = models.BooleanField(_("Can Manage Orders"), default=False)

    class Meta:
        verbose_name = _("Predefined Admin Right")
        verbose_name_plural = _("Predefined Admin Rights")
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class EmailVerificationToken(models.Model):
    """Model to store email verification tokens for user activation."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="verification_tokens", verbose_name=_("User"))
    token = models.UUIDField(_("Token"), default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    expires_at = models.DateTimeField(_("Expires At"))

    class Meta:
        verbose_name = _("Email Verification Token")
        verbose_name_plural = _("Email Verification Tokens")
        indexes = [
            models.Index(fields=['token']),
        ]

    def is_valid(self):
        return timezone.now() < self.expires_at

    def send_verification_email(self):
        """Send email verification to the user."""
        verification_url = reverse('verify-email', kwargs={'token': self.token})
        full_url = f"{settings.SITE_URL}{verification_url}"
        subject = _("Verify Your Email Address")
        message = _("Click the following link to verify your email: {0}").format(full_url)
        self.user.email_user(subject, message)

    def __str__(self):
        return f"Verification token for {self.user.email}"


class UserActivityLog(models.Model):
    """Logs model to store user activities for audit and compliance purposes."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name=_("User"))
    action = models.CharField(_("Action"), max_length=255)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_("IP Address"), null=True, blank=True)
    additional_data = models.JSONField(_("Additional Data"), null=True, blank=True)

    class Meta:
        verbose_name = _("User Activity Log")
        verbose_name_plural = _("User Activity Logs")
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"Activity by {self.user.email} on {self.timestamp}"
