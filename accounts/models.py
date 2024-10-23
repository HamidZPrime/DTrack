# accounts/models.py

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Permission,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.core.validators import RegexValidator
from datetime import timedelta
import uuid


class CustomUserManager(BaseUserManager):
    """
    Custom manager for handling the creation of different user roles.
    Includes helper methods to create standard users and superusers.
    """

    def create_user(self, email: str, password: str = None, **extra_fields) -> "CustomUser":
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_active = False  # Keep inactive until email verification
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str = None, **extra_fields) -> "CustomUser":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        user = self.create_user(email, password, **extra_fields)
        user.is_active = True  # Superusers are active by default
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("admin", _("Admin")),
        ("operator", _("Operator")),
        ("supplier", _("Supplier")),
        ("enduser", _("End User")),
    )

    APPROVAL_CHOICES = (
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    )

    email = models.EmailField(
        _("Email Address"), unique=True, max_length=255, db_index=True
    )
    role = models.CharField(
        _("Role"), max_length=50, choices=ROLE_CHOICES, default="enduser"
    )
    first_name = models.CharField(_("First Name"), max_length=50, blank=True)
    last_name = models.CharField(
        _("Last Name"), max_length=50, blank=True, null=True
    )
    phone_number = models.CharField(
        _("Phone Number"),
        max_length=15,
        blank=True,
        null=True,  # Allow NULL values in the database
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', _("Enter a valid phone number."))],
    )
    is_active = models.BooleanField(_("Active"), default=False)
    is_staff = models.BooleanField(_("Staff Status"), default=False)
    is_superuser = models.BooleanField(_("Superuser Status"), default=False)
    language = models.CharField(
        _("Language"),
        max_length=5,
        default="en",
        choices=settings.LANGUAGES,
    )
    date_joined = models.DateTimeField(_("Date Joined"), default=timezone.now)

    email_verified = models.BooleanField(_("Email Verified"), default=False)
    profile_complete = models.BooleanField(_("Profile Complete"), default=False)
    is_approved = models.BooleanField(_("Approved"), default=False)
    approval_status = models.CharField(
        _("Approval Status"),
        max_length=20,
        choices=APPROVAL_CHOICES,
        default="pending",
    )

    supplier_qr = models.OneToOneField(
        "qr_generator.SupplierQR",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplier_user",
        verbose_name=_("Supplier QR Code"),
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["approval_status"]),
        ]

    def __str__(self):
        return self.email

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self) -> str:
        return self.first_name

    def email_user(self, subject: str, message: str, from_email: str = None, **kwargs) -> None:
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def save(self, *args, **kwargs) -> None:
        self.email = self.email.lower()
        super().save(*args, **kwargs)


def check_certificate_expiration(self) -> None:
    if self.role == "supplier":
        expired_certificates = self.certificate_set.filter(
            expiry_date__lt=timezone.now().date(), approved=True
        ).exists()

        new_is_active = not expired_certificates
        if self.is_active != new_is_active:
            self.is_active = new_is_active
            self.save(update_fields=['is_active'])


CustomUser.check_certificate_expiration = check_certificate_expiration


class OperatorPermission(models.Model):
    operator = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "operator"},
        verbose_name=_("Operator"),
    )
    app_level_permissions = models.ManyToManyField(
        Permission, verbose_name=_("App-Level Permissions"), blank=True
    )
    view_only = models.BooleanField(_("View Only"), default=False)

    class Meta:
        verbose_name = _("Operator Permission")
        verbose_name_plural = _("Operator Permissions")

    def __str__(self) -> str:
        return f"Permissions for {self.operator.get_full_name()}"


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="verification_tokens",
        verbose_name=_("User"),
    )
    token = models.UUIDField(
        _("Token"), default=uuid.uuid4, unique=True, editable=False
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    expires_at = models.DateTimeField(_("Expires At"))

    class Meta:
        verbose_name = _("Email Verification Token")
        verbose_name_plural = _("Email Verification Tokens")
        indexes = [
            models.Index(fields=["token"]),
        ]

    def is_valid(self) -> bool:
        return timezone.now() < self.expires_at

    def send_verification_email(self) -> None:
        verification_url = reverse("verify-email", kwargs={"token": self.token})
        full_url = f"{settings.SITE_URL}{verification_url}"
        subject = _("Verify Your Email Address")
        message = _("Click the following link to verify your email: {0}").format(full_url)
        self.user.email_user(subject, message)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)  # Token valid for 24 hours
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Verification token for {self.user.email}"


class UserActivityLog(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name=_("User")
    )
    action = models.CharField(_("Action"), max_length=255)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_("IP Address"), null=True, blank=True)
    additional_data = models.JSONField(_("Additional Data"), null=True, blank=True)

    class Meta:
        verbose_name = _("User Activity Log")
        verbose_name_plural = _("User Activity Logs")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["timestamp"]),
        ]

    def __str__(self) -> str:
        return f"Activity by {self.user.email} on {self.timestamp}"


# Signals for CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def handle_user_post_save(sender, instance, created, **kwargs):
    if instance.is_superuser and not instance.is_active:
        instance.is_active = True
        instance.save(update_fields=['is_active'])

    if instance.role == "supplier":
        instance.check_certificate_expiration()

    if instance.role in ["supplier", "operator", "enduser"] and instance.approval_status == "approved":
        if not instance.is_approved:
            instance.is_approved = True
            instance.save(update_fields=['is_approved'])

    if instance.role == "supplier" and instance.is_approved and not instance.supplier_qr:
        from qr_generator.models import SupplierQR

        supplier_qr = SupplierQR.objects.create(supplier=instance)
        instance.supplier_qr = supplier_qr
        instance.save(update_fields=['supplier_qr'])


@receiver(post_save, sender=CustomUser)
def log_user_save(sender, instance, created, **kwargs):
    action = "created" if created else "updated"
    UserActivityLog.objects.create(
        user=instance,
        action=f"User {instance.email} {action}",
        ip_address=None,  # Adjust this if you have access to the IP address
        additional_data={"user_id": instance.id},
    )
