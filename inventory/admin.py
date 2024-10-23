from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from approval.models import ApprovalStatus
from .models import Category, Tag, Product
from qr_generator.models import ProductQR
from django.utils.html import format_html


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface to manage Categories.
    """

    list_display = ("name", "date_created")
    search_fields = ("name",)
    readonly_fields = ("date_created",)

    fieldsets = ((None, {"fields": ("name", "description", "date_created")}),)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin interface to manage Tags.
    """

    list_display = ("name", "date_created")
    search_fields = ("name",)
    readonly_fields = ("date_created",)

    fieldsets = ((None, {"fields": ("name", "description", "date_created")}),)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin interface to manage Products.
    """

    list_display = (
        "name",
        "supplier",
        "category",
        "price",
        "quantity_in_stock",
        "approved",
        "get_qr_code_image",
        "date_added",
        "last_updated",
    )
    list_filter = (
        "category",
        "approved",
        "approval_status",
        "date_added",
        "last_updated",
    )
    search_fields = (
        "name",
        "supplier__email",
        "supplier__first_name",
        "supplier__last_name",
        "sku",
    )
    readonly_fields = ("get_qr_code_image", "date_added", "last_updated", "product_qr")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "supplier",
                    "name",
                    "description",
                    "category",
                    "tags",
                    "sku",
                    "price",
                    "cost",
                    "quantity_in_stock",
                )
            },
        ),
        (
            _("Images"),
            {
                "fields": (
                    "image_1",
                    "image_2",
                    "image_3",
                    "image_4",
                    "image_5",
                    "image_6",
                )
            },
        ),
        (
            _("Sustainability & Origin"),
            {
                "fields": (
                    "origin_country",
                    "material_source",
                    "carbon_footprint",
                    "lifecycle_assessment",
                    "sustainability_certificates",
                )
            },
        ),
        (_("Product Lifecycle"), {"fields": ("production_date", "warranty_period")}),
        (
            _("Approval & QR Code"),
            {
                "fields": (
                    "approval_status",
                    "approved",
                    "get_qr_code_image",
                    "product_qr",
                )
            },
        ),
        (_("Dates"), {"fields": ("date_added", "last_updated")}),
    )

    def get_qr_code_image(self, obj):
        """
        Display the QR code image for the product.
        """
        if obj.product_qr and obj.product_qr.qr_code_image:
            return format_html(
                f'<img src="{obj.product_qr.qr_code_image.url}" width="100" height="100" />'
            )
        return _("No QR Code")

    get_qr_code_image.short_description = _("QR Code Image")

    def save_model(self, request, obj, form, change):
        """
        Override the save method to update QR code generation based on changes.
        """
        if obj.approval_status == ApprovalStatus.APPROVED and not obj.product_qr:
            product_qr = ProductQR.objects.create(
                supplier=obj.supplier, product_id=obj.pk
            )
            obj.product_qr = product_qr
            obj.product_qr.generate_qr_code()

        super().save_model(request, obj, form, change)
