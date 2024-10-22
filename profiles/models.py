from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Profile(models.Model):
    """
    Comprehensive Profile model to store additional information for each user type (Admin, Operator, Supplier, EndUser).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("User")
    )

    # Common fields for all profiles
    date_of_birth = models.DateField(_("Date of Birth"), null=True, blank=True)
    address = models.CharField(_("Address"), max_length=255, blank=True)
    city = models.CharField(_("City"), max_length=50, blank=True)
    country = models.CharField(_("Country"), max_length=50, blank=True)
    postal_code = models.CharField(_("Postal Code"), max_length=10, blank=True)
    profile_picture = models.ImageField(_("Profile Picture"), upload_to='profiles/pictures/', null=True, blank=True)
    phone_verified = models.BooleanField(_("Phone Verified"), default=False)

    # Supplier-specific fields
    company_name = models.CharField(_("Company Name"), max_length=255, blank=True)
    company_registration_number = models.CharField(_("Company Registration Number"), max_length=50, blank=True)
    vat_number = models.CharField(_("VAT Number"), max_length=50, blank=True)
    supplier_type = models.CharField(_("Supplier Type"), max_length=50, blank=True,
                                     help_text=_("E.g., Manufacturer, Distributor"))
    industry = models.CharField(_("Industry"), max_length=50, blank=True)

    # Admin-specific fields
    admin_notes = models.TextField(_("Admin Notes"), blank=True)

    # Operator-specific fields
    operator_level = models.PositiveIntegerField(
        _("Operator Level"),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_("1-5, with 5 being the highest rank.")
    )

    # End user-specific fields
    preferred_language = models.CharField(
        _("Preferred Language"),
        max_length=5,
        choices=[('en', 'English'), ('ar', 'Arabic')],
        default='en'
    )
    interests = models.TextField(
        _("Interests"),
        blank=True,
        help_text=_("E.g., Jewelry, Gold, Fashion")
    )

    # Additional fields
    profile_complete = models.BooleanField(_("Profile Complete"), default=False)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    date_updated = models.DateTimeField(_("Date Updated"), auto_now=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Profile of {self.user.get_full_name()}" if hasattr(self.user, 'get_full_name') else "Profile"

    def mark_complete(self):
        """
        Method to mark the profile as complete after all required fields are filled.
        """
        # Define the required fields based on the user role
        required_fields = ['address', 'city', 'country', 'date_of_birth']

        if getattr(self.user, 'role', '') == 'supplier':
            required_fields.append('company_name')

        # Check if all required fields are filled
        for field in required_fields:
            if not getattr(self, field):
                return False

        self.profile_complete = True
        self.save()
        return True
