from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.mail import send_mail

import accounts.models


class TicketDepartment(models.Model):
    """
    Model to define ticket departments.
    E.g., Technical, Sales, Compliance, Certificate, etc.
    """
    name = models.CharField(_("Department Name"), max_length=50, unique=True)
    description = models.TextField(_("Description"), blank=True)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Ticket Department")
        verbose_name_plural = _("Ticket Departments")

    def __str__(self):
        return self.name


class TicketCategory(models.Model):
    """
    Model to define categories within departments.
    E.g., Technical > Software, Hardware, Networking, etc.
    """
    department = models.ForeignKey(TicketDepartment, on_delete=models.CASCADE, related_name="categories", verbose_name=_("Department"))
    name = models.CharField(_("Category Name"), max_length=50)
    description = models.TextField(_("Description"), blank=True)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Ticket Category")
        verbose_name_plural = _("Ticket Categories")
        unique_together = ('department', 'name')

    def __str__(self):
        return f"{self.department.name} - {self.name}"


class Ticket(models.Model):
    """
    Model to represent a support ticket created by a supplier.
    """
    STATUS_CHOICES = [
        ('open', _("Open")),
        ('in_progress', _("In Progress")),
        ('awaiting_user', _("Awaiting User Response")),
        ('awaiting_support', _("Awaiting Support Response")),
        ('resolved', _("Resolved")),
        ('closed', _("Closed")),
        ('escalated', _("Escalated")),
    ]

    PRIORITY_CHOICES = [
        ('low', _("Low")),
        ('medium', _("Medium")),
        ('high', _("High")),
        ('critical', _("Critical")),
    ]

    supplier = models.ForeignKey(
        accounts.models.CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'supplier'},
        related_name="tickets",
        verbose_name=_("Supplier")
    )
    department = models.ForeignKey(
        TicketDepartment,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tickets",
        verbose_name=_("Department")
    )
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tickets",
        verbose_name=_("Category"),
        help_text=_("Sub-category within the selected department.")
    )
    title = models.CharField(_("Ticket Title"), max_length=255)
    description = models.TextField(_("Description"))
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(_("Priority"), max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(
        accounts.models.CustomUser,
        on_delete=models.SET_NULL,
        limit_choices_to={'role': 'operator'},
        related_name="assigned_tickets",
        null=True,
        blank=True,
        verbose_name=_("Assigned Operator")
    )
    sla_due_date = models.DateTimeField(_("SLA Due Date"), null=True, blank=True)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    last_updated = models.DateTimeField(_("Last Updated"), auto_now=True)

    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")
        indexes = [
            models.Index(fields=['supplier']),
            models.Index(fields=['department']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"Ticket #{self.pk} - {self.title}"

    def send_notification(self, event):
        """
        Sends email notifications based on the event (ticket creation, status change, etc.).
        """
        subject = f"[{self.get_status_display()}] - Ticket #{self.pk}: {self.title}"
        message = f"Ticket Update:\n\nTitle: {self.title}\nStatus: {self.get_status_display()}\nPriority: {self.get_priority_display()}\nDescription: {self.description}\n\nPlease login to view more details."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = []

        if event == 'created':
            # Notify supplier
            recipient_list.append(self.supplier.email)

        if event in ['created', 'status_changed', 'assigned']:
            # Notify all department operators
            department_operators = accounts.models.CustomUser.objects.filter(role='operator', operatorpermission__can_manage_tickets=True, profile__department=self.department)
            for operator in department_operators:
                recipient_list.append(operator.email)

        if recipient_list:
            send_mail(subject, message, from_email, recipient_list)

    def save(self, *args, **kwargs):
        """
        Override save method to handle notifications and automatic actions.
        """
        is_new = self.pk is None
        previous_status = None
        if not is_new:
            previous_status = Ticket.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        if is_new:
            self.send_notification(event='created')
        elif self.status != previous_status:
            self.send_notification(event='status_changed')


class TicketAttachment(models.Model):
    """
    Model to handle attachments for a ticket.
    """
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name=_("Ticket")
    )
    attachment = models.FileField(_("Attachment"), upload_to='tickets/attachments/', null=True, blank=True)
    date_added = models.DateTimeField(_("Date Added"), auto_now_add=True)

    class Meta:
        verbose_name = _("Ticket Attachment")
        verbose_name_plural = _("Ticket Attachments")
        indexes = [
            models.Index(fields=['ticket']),
        ]

    def __str__(self):
        return f"Attachment for Ticket #{self.ticket.pk}"


class TicketReply(models.Model):
    """
    Model to handle replies for tickets.
    """
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name=_("Ticket")
    )
    author = models.ForeignKey(
        accounts.models.CustomUser,
        on_delete=models.CASCADE,
        related_name="ticket_replies",
        verbose_name=_("Author")
    )
    message = models.TextField(_("Message"))
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    last_updated = models.DateTimeField(_("Last Updated"), auto_now=True)

    class Meta:
        verbose_name = _("Ticket Reply")
        verbose_name_plural = _("Ticket Replies")
        indexes = [
            models.Index(fields=['ticket']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return f"Reply #{self.pk} for Ticket #{self.ticket.pk}"


class ReplyAttachment(models.Model):
    """
    Model to handle attachments for a ticket reply.
    """
    reply = models.ForeignKey(
        TicketReply,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name=_("Reply")
    )
    attachment = models.FileField(_("Attachment"), upload_to='replies/attachments/', null=True, blank=True)
    date_added = models.DateTimeField(_("Date Added"), auto_now_add=True)

    class Meta:
        verbose_name = _("Reply Attachment")
        verbose_name_plural = _("Reply Attachments")
        indexes = [
            models.Index(fields=['reply']),
        ]

    def __str__(self):
        return f"Attachment for Reply #{self.reply.pk}"
