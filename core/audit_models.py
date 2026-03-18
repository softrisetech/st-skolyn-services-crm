from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
import uuid


class ActivityLog(models.Model):
    """
    Single table to log all CREATE/UPDATE/DELETE operations across the entire project
    """
    
    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]
    
    # ✅ UUID primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    
    # What was changed (which model)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        verbose_name=_('content type')
    )
    
    # ✅ UUID of the object that was changed
    object_id = models.UUIDField(db_index=True, verbose_name=_('object id'))
    
    # Model name stored directly (e.g., "Class", "Subject", "Section")
    model_name = models.CharField(max_length=100, db_index=True, verbose_name=_('model name'))
    
    # Action type (create/update/delete)
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        verbose_name=_('action'),
        db_index=True
    )
    
    # Changes (JSON) - stores what changed in updates
    changes = models.JSONField(null=True, blank=True, verbose_name=_('changes'))
    
    # Custom fields - business_id is OPTIONAL (nullable)
    business_id = models.UUIDField(null=True, blank=True, db_index=True, verbose_name=_('business id'))
    auth_id = models.UUIDField(null=True, blank=True, db_index=True, verbose_name=_('auth id'))
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('timestamp'))
    remote_addr = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('remote address'))
    
    class Meta:
        app_label = 'leads'
        db_table = 'activity_log'
        ordering = ['-timestamp']
        verbose_name = _('activity log')
        verbose_name_plural = _('activity logs')
        indexes = [
            models.Index(fields=['business_id', 'timestamp']),
            models.Index(fields=['auth_id', 'timestamp']),
            models.Index(fields=['model_name', 'timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f'{self.action} - {self.model_name} - {self.timestamp}'
    
    @property
    def changes_dict(self):
        """Return changes as a formatted dictionary"""
        if self.changes:
            return self.changes
        return {}