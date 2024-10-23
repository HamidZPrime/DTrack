from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator
from approval.models import ApprovalStatus  # Import approval status choices
from qr_generator.models import (
    ProductQR,
)  # Import QR code model for product integration
from certificates.models import Certificate


class Category(models.Model):
    """
    Model to define product categories.
    """

    name = models.CharField(_("Category Name"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Model to define product tags for discoverability.
    """

    name = models.CharField(_("Tag Name"), max_length=255, unique=True)
    description = models.TextField(_("Description"), blank=True)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Comprehensive product model to store all the information related to a product.
    Includes sustainability information, pricing, and inventory management.
    """

    supplier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "supplier"},
        related_name="products",
        verbose_name=_("Supplier"),
    )
    name = models.CharField(_("Product Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
        verbose_name=_("Category"),
    )
    tags = models.ManyToManyField(
        Tag, related_name="products", verbose_name=_("Tags"), blank=True
    )
    sku = models.CharField(_("SKU"), max_length=100, unique=True)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    cost = models.DecimalField(
        _("Cost"), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    quantity_in_stock = models.PositiveIntegerField(_("Quantity in Stock"), default=0)

    # Images (up to 6 images)
    image_1 = models.ImageField(
        _("Image 1"), upload_to="products/images/", null=True, blank=True
    )
    image_2 = models.ImageField(
        _("Image 2"), upload_to="products/images/", null=True, blank=True
    )
    image_3 = models.ImageField(
        _("Image 3"), upload_to="products/images/", null=True, blank=True
    )
    image_4 = models.ImageField(
        _("Image 4"), upload_to="products/images/", null=True, blank=True
    )
    image_5 = models.ImageField(
        _("Image 5"), upload_to="products/images/", null=True, blank=True
    )
    image_6 = models.ImageField(
        _("Image 6"), upload_to="products/images/", null=True, blank=True
    )

    # Sustainability and origin information
    origin_country = models.CharField(_("Country of Origin"), max_length=50, blank=True)
    material_source = models.CharField(
        _("Material Source"),
        max_length=255,
        blank=True,
        help_text=_("Where the materials are sourced from."),
    )
    carbon_footprint = models.DecimalField(
        _("Carbon Footprint (kg CO2e)"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_(
            "Carbon footprint in kg CO2 equivalent for the product's lifecycle."
        ),
        null=True,
        blank=True,
    )
    lifecycle_assessment = models.TextField(
        _("Lifecycle Assessment"),
        blank=True,
        help_text=_(
            "A description of the product's lifecycle, from raw material extraction to end-of-life."
        ),
    )

    # Sustainability Certificates from approved list
    sustainability_certificates = models.ManyToManyField(
        Certificate,
        blank=True,
        limit_choices_to={"approval_status": ApprovalStatus.APPROVED},
        verbose_name=_("Sustainability Certificates"),
        help_text=_("Select from approved certificates."),
    )

    # Product lifecycle information
    production_date = models.DateField(_("Production Date"), null=True, blank=True)
    warranty_period = models.PositiveIntegerField(
        _("Warranty Period (months)"),
        default=0,
        help_text=_("Warranty period in months."),
    )

    # Approval fields
    approval_status = models.CharField(
        _("Approval Status"),
        max_length=10,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )
    approved = models.BooleanField(_("Approved"), default=False)

    # QR Code integration
    product_qr = models.OneToOneField(
        ProductQR,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product",
        verbose_name=_("Product QR Code"),
    )

    date_added = models.DateTimeField(_("Date Added"), auto_now_add=True)
    last_updated = models.DateTimeField(_("Last Updated"), auto_now=True)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        indexes = [
            models.Index(fields=["supplier"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["approval_status"]),
        ]

    def __str__(self):
        return self.name

    def generate_product_qr(self):
        """
        Method to create a QR code for a product.
        """
        if not self.product_qr and self.approval_status == ApprovalStatus.APPROVED:
            product_qr = ProductQR.objects.create(product=self)
            self.product_qr = product_qr
            self.save()

    def save(self, *args, **kwargs):
        """
        Override save method to ensure QR code generation and approval updates.
        """
        if self.approval_status == ApprovalStatus.APPROVED:
            self.approved = True
            self.generate_product_qr()
        else:
            self.approved = False
        super().save(*args, **kwargs)
