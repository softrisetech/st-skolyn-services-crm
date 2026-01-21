import uuid
from django.db import models
from autoslug import AutoSlugField
from core.base_models import BaseModel
from core.constants.model_constants import *

class Module(BaseModel):
    app_id = models.UUIDField(null=True, db_index=True)
    app_slug = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    name = models.CharField(max_length=CHAR_LENGTH)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, null=True)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, null=True)
    is_active = models.BooleanField(default=True)

class Permission(BaseModel):
    module = models.ForeignKey(
        'Module',
        on_delete=models.CASCADE,
        related_name='permissions',  # Add related_name here
        null=False,
        db_index=True
    )
    name = models.CharField(max_length=CHAR_LENGTH)
    url = models.TextField(max_length=LONG_CHAR_LENGTH, null=True, blank=True)
    frontend_url = models.TextField(max_length=LONG_CHAR_LENGTH, null=True, blank=True)
    request_method = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    key = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    type = models.PositiveSmallIntegerField(null=False)
    sort_order = models.PositiveSmallIntegerField(null=False)
    is_active = models.BooleanField(default=True)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, null=True, blank=True)

    class Meta:
        ordering = ['sort_order']

    def get_module(self):
        try:
            module = Module.objects.get(id=self.module_id)
            return module
        except Module.DoesNotExist:
            return None

class RolePermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role_id = models.UUIDField(null=False, db_index=True)
    permission = models.ForeignKey('Permission', on_delete=models.CASCADE, null=False, db_index=True)
