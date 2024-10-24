# Generated by Django 5.1.2 on 2024-10-24 19:24

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_of_birth",
                    models.DateField(
                        blank=True, null=True, verbose_name="Date of Birth"
                    ),
                ),
                (
                    "address",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Address"
                    ),
                ),
                (
                    "city",
                    models.CharField(blank=True, max_length=50, verbose_name="City"),
                ),
                (
                    "country",
                    models.CharField(blank=True, max_length=50, verbose_name="Country"),
                ),
                (
                    "postal_code",
                    models.CharField(
                        blank=True, max_length=10, verbose_name="Postal Code"
                    ),
                ),
                (
                    "profile_picture",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="profiles/pictures/",
                        verbose_name="Profile Picture",
                    ),
                ),
                (
                    "phone_verified",
                    models.BooleanField(default=False, verbose_name="Phone Verified"),
                ),
                (
                    "company_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Company Name"
                    ),
                ),
                (
                    "company_registration_number",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        verbose_name="Company Registration Number",
                    ),
                ),
                (
                    "vat_number",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="VAT Number"
                    ),
                ),
                (
                    "supplier_type",
                    models.CharField(
                        blank=True,
                        help_text="E.g., Manufacturer, Distributor",
                        max_length=50,
                        verbose_name="Supplier Type",
                    ),
                ),
                (
                    "industry",
                    models.CharField(
                        blank=True, max_length=50, verbose_name="Industry"
                    ),
                ),
                (
                    "admin_notes",
                    models.TextField(blank=True, verbose_name="Admin Notes"),
                ),
                (
                    "operator_level",
                    models.PositiveIntegerField(
                        default=1,
                        help_text="1-5, with 5 being the highest rank.",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(5),
                        ],
                        verbose_name="Operator Level",
                    ),
                ),
                (
                    "preferred_language",
                    models.CharField(
                        choices=[("en", "English"), ("ar", "Arabic")],
                        default="en",
                        max_length=5,
                        verbose_name="Preferred Language",
                    ),
                ),
                (
                    "interests",
                    models.TextField(
                        blank=True,
                        help_text="E.g., Jewelry, Gold, Fashion",
                        verbose_name="Interests",
                    ),
                ),
                (
                    "profile_complete",
                    models.BooleanField(default=False, verbose_name="Profile Complete"),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Date Created"
                    ),
                ),
                (
                    "date_updated",
                    models.DateTimeField(auto_now=True, verbose_name="Date Updated"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Profile",
                "verbose_name_plural": "Profiles",
                "indexes": [
                    models.Index(fields=["user"], name="profiles_pr_user_id_3364d1_idx")
                ],
            },
        ),
    ]
