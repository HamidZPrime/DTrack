from django.contrib import admin
from .models import FileCategory, FileRecord, FileLog

@admin.register(FileCategory)
class FileCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(FileRecord)
class FileRecordAdmin(admin.ModelAdmin):
    list_display = ('file', 'category', 'uploaded_by', 'get_user_email', 'timestamp', 'last_accessed',)
    list_filter = ('uploaded_by', 'category',)
    search_fields = ('file', 'description', 'uploaded_by__email', 'uploaded_by__first_name', 'uploaded_by__last_name',)
    ordering = ('-timestamp',)
    readonly_fields = ('uuid', 'last_accessed', 'timestamp',)
    list_per_page = 20

    def get_user_email(self, obj):
        return obj.uploaded_by.email if obj.uploaded_by else 'System'
    get_user_email.short_description = 'Uploaded By (Email)'

    @staticmethod
    def view_on_site(obj):
        if obj.file:
            return obj.file.url
        return None

    def save_model(self, request, obj, form, change):
        if change:
            # Add a log entry for update
            FileLog.objects.create(file_record=obj, user=request.user, action='update', additional_data={'description': obj.description})
        else:
            # Add a log entry for upload
            FileLog.objects.create(file_record=obj, user=request.user, action='upload', additional_data={'description': obj.description})
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        # Add a log entry for delete
        FileLog.objects.create(file_record=obj, user=request.user, action='delete')
        super().delete_model(request, obj)


@admin.register(FileLog)
class FileLogAdmin(admin.ModelAdmin):
    list_display = ('file_record', 'action', 'user', 'timestamp',)
    list_filter = ('action', 'timestamp',)
    search_fields = ('file_record__file', 'user__email', 'user__first_name', 'user__last_name',)
    ordering = ('-timestamp',)
