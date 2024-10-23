from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


class FileCategory(models.Model):
    """
    Model to categorize files based on their purpose.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class FileRecord(models.Model):
    """
    Comprehensive model to handle files uploaded by users, with categories, logs, and access controls.
    """

    file = models.FileField(upload_to="uploads/")
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        FileCategory, on_delete=models.SET_NULL, null=True, related_name="files"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return self.file.name if self.file else "No File"


class FileLog(models.Model):
    """
    Model to track file-related activities such as upload, update, or deletion.
    """

    file_record = models.ForeignKey(
        FileRecord, on_delete=models.CASCADE, related_name="logs"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Log for {self.file_record.file.name if self.file_record.file else 'No File'}"
