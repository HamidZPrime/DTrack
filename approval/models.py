from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser


class ApprovalStatus(models.TextChoices):
    """Choices for the status of the approval."""

    PENDING = "pending", _("Pending")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")


class ApprovalType(models.TextChoices):
    """Choices for the type of entity to be approved."""

    SUPPLIER = "supplier", _("Supplier")
    CERTIFICATE = "certificate", _("Certificate")
    PRODUCT = "product", _("Product")
    OTHER = "other", _("Other")


class ApprovalRequest(models.Model):
    """
    Model to manage the approval process for suppliers, certificates, products, etc.
    Admins can review and approve or reject these entities.
    """

    requester = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="approval_requests",
        verbose_name=_("Requester"),
    )
    entity_type = models.CharField(
        _("Entity Type"), max_length=50, choices=ApprovalType.choices
    )
    entity_id = models.PositiveIntegerField(
        _("Entity ID")
    )  # Entity ID refers to the primary key of the entity table
    status = models.CharField(
        _("Approval Status"),
        max_length=10,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )
    reviewed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approvals_reviewed",
        verbose_name=_("Reviewed By"),
    )
    reviewed_at = models.DateTimeField(_("Reviewed At"), null=True, blank=True)
    request_time = models.DateTimeField(_("Request Time"), auto_now_add=True)
    comments = models.TextField(_("Comments"), blank=True)

    class Meta:
        verbose_name = _("Approval Request")
        verbose_name_plural = _("Approval Requests")
        indexes = [
            models.Index(fields=["entity_id", "entity_type"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Approval Request for {self.entity_type} - {self.status}"


class ApprovalLog(models.Model):
    """
    Model to store logs of approval actions for auditing and compliance purposes.
    Logs each change in approval status, the entity type, and the reviewer responsible.
    """

    approval_request = models.ForeignKey(
        ApprovalRequest,
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name=_("Approval Request"),
    )
    previous_status = models.CharField(
        _("Previous Status"), max_length=10, choices=ApprovalStatus.choices
    )
    new_status = models.CharField(
        _("New Status"), max_length=10, choices=ApprovalStatus.choices
    )
    action_taken_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="approval_actions",
        verbose_name=_("Action Taken By"),
    )
    action_time = models.DateTimeField(_("Action Time"), auto_now_add=True)
    comments = models.TextField(_("Comments"), blank=True)

    class Meta:
        verbose_name = _("Approval Log")
        verbose_name_plural = _("Approval Logs")
        indexes = [
            models.Index(fields=["approval_request"]),
            models.Index(fields=["action_time"]),
        ]

    def __str__(self):
        return f"Approval Log for {self.approval_request.entity_type} - {self.new_status} at {self.action_time}"


class ApprovalAction(models.Model):
    """
    Model to define specific actions admins can take during the approval process.
    These actions can be tied to workflows and custom rules.
    """

    name = models.CharField(_("Action Name"), max_length=50, unique=True)
    description = models.TextField(_("Description"), blank=True)
    is_default = models.BooleanField(_("Is Default Action"), default=False)

    class Meta:
        verbose_name = _("Approval Action")
        verbose_name_plural = _("Approval Actions")
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name
