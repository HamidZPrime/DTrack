from django.contrib import admin
from .models import TemplateCategory, EmailTemplate, SMSTemplate, VoiceTemplate, TemplateTag, TemplateUsage

@admin.register(TemplateCategory)
class TemplateCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'category', 'created_by')
    search_fields = ('name', 'subject', 'category__name')
    list_filter = ('category',)
    fieldsets = (
        (None, {
            'fields': ('name', 'subject', 'html_body', 'text_body', 'category', 'created_by')
        }),
    )


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'category', 'created_by')
    search_fields = ('name', 'body', 'category__name')
    list_filter = ('category',)
    fieldsets = (
        (None, {
            'fields': ('name', 'body', 'category', 'created_by')
        }),
    )


@admin.register(VoiceTemplate)
class VoiceTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'message_file', 'description', 'category', 'created_by')
    search_fields = ('name', 'description', 'category__name')
    list_filter = ('category',)
    fieldsets = (
        (None, {
            'fields': ('name', 'message_file', 'description', 'category', 'created_by')
        }),
    )


@admin.register(TemplateTag)
class TemplateTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(TemplateUsage)
class TemplateUsageAdmin(admin.ModelAdmin):
    list_display = ('template_name', 'used_in', 'used_at', 'used_by')
    search_fields = ('template_name', 'used_in', 'used_by__email')
    list_filter = ('used_in', 'used_at')
    readonly_fields = ('used_at',)
