from django.db import models
from core.constants.model_constants import *
from core.base_models import BaseBusinessModel

class Export(BaseBusinessModel):
    app_slug = models.CharField(max_length=CHAR_LENGTH)
    type = models.CharField(max_length=CHAR_LENGTH)
    status = models.CharField(max_length=CHAR_LENGTH)
    created_by = models.UUIDField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    link = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    file_name = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    class Meta:
        db_table = 'report_export'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['app_slug'], name='idx_app_slug'),
        ]
