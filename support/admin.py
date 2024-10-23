from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import TicketDepartment, TicketCategory, Ticket, TicketAttachment, TicketReply, ReplyAttachment

class TicketDepartmentAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Ticket Departments.
    """
    list_display = ('name', 'date_created')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('date_created',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        (_('Important Dates'), {
            'fields': ('date_created',),
        }),
    )

admin.site.register(TicketDepartment, TicketDepartmentAdmin)


class TicketCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Ticket Categories.
    """
    list_display = ('name', 'department', 'date_created')
    search_fields = ('name', 'department__name')
    ordering = ('department', 'name')
    readonly_fields = ('date_created',)
    fieldsets = (
        (None, {
            'fields': ('department', 'name', 'description')
        }),
        (_('Important Dates'), {
            'fields': ('date_created',),
        }),
    )

admin.site.register(TicketCategory, TicketCategoryAdmin)


class TicketAttachmentInline(admin.TabularInline):
    """
    Inline interface for managing ticket attachments within a ticket.
    """
    model = TicketAttachment
    extra = 1
    readonly_fields = ('date_added',)
    fields = ('attachment', 'date_added')


class TicketReplyInline(admin.TabularInline):
    """
    Inline interface for managing replies within a ticket.
    """
    model = TicketReply
    extra = 1
    readonly_fields = ('date_created', 'last_updated')
    fields = ('author', 'message', 'date_created', 'last_updated')


class TicketAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Tickets.
    """
    list_display = ('title', 'supplier', 'status', 'priority', 'department', 'category', 'assigned_to', 'date_created')
    list_filter = ('status', 'priority', 'department', 'assigned_to')
    search_fields = ('title', 'supplier__email', 'assigned_to__email')
    ordering = ('-date_created',)
    readonly_fields = ('date_created', 'last_updated')
    fieldsets = (
        (None, {
            'fields': ('supplier', 'title', 'description')
        }),
        (_('Department and Category'), {
            'fields': ('department', 'category')
        }),
        (_('Ticket Details'), {
            'fields': ('status', 'priority', 'assigned_to', 'sla_due_date')
        }),
        (_('Important Dates'), {
            'fields': ('date_created', 'last_updated')
        }),
    )
    inlines = [TicketReplyInline, TicketAttachmentInline]

admin.site.register(Ticket, TicketAdmin)


class TicketReplyAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Ticket Replies.
    """
    list_display = ('ticket', 'author', 'date_created', 'last_updated')
    search_fields = ('ticket__title', 'author__email')
    ordering = ('-date_created',)
    readonly_fields = ('date_created', 'last_updated')
    fieldsets = (
        (None, {
            'fields': ('ticket', 'author', 'message')
        }),
        (_('Important Dates'), {
            'fields': ('date_created', 'last_updated'),
        }),
    )

admin.site.register(TicketReply, TicketReplyAdmin)


class ReplyAttachmentAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Reply Attachments.
    """
    list_display = ('reply', 'date_added')
    search_fields = ('reply__ticket__title', 'reply__author__email')
    ordering = ('-date_added',)
    readonly_fields = ('date_added',)
    fieldsets = (
        (None, {
            'fields': ('reply', 'attachment')
        }),
        (_('Important Dates'), {
            'fields': ('date_added',),
        }),
    )

admin.site.register(ReplyAttachment, ReplyAttachmentAdmin)
