import uuid
from django.db import models
from autoslug import AutoSlugField
from core.base_models import BaseModel
from core.constants.model_constants import CHAR_LENGTH, LONG_CHAR_LENGTH

class Module(BaseModel):
    app_id = models.UUIDField(null=True, db_index=True)
    app_slug = models.CharField(max_length=CHAR_LENGTH, blank=True)
    name = models.CharField(max_length=CHAR_LENGTH)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, null=True)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField()

class Permission(BaseModel):
    module = models.ForeignKey(
        'Module',
        on_delete=models.CASCADE,
        related_name='permissions',  # Add related_name here
        null=False,
        db_index=True
    )
    name = models.CharField(max_length=CHAR_LENGTH, null=False, blank=False)
    url = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)
    frontend_url = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)
    request_method = models.CharField(max_length=CHAR_LENGTH, blank=True)
    key = models.CharField(max_length=CHAR_LENGTH, blank=True)
    type = models.PositiveSmallIntegerField(null=False, blank=False)
    sort_order = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)

    class Meta:
        ordering = ['sort_order']

    def get_module(self):
        try:
            module = Module.objects.get(id=self.module_id)
            return module
        except Module.DoesNotExist:
            return None

class RolePermission(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    role_id = models.UUIDField(null=False, db_index=True)
    permission = models.ForeignKey('Permission', on_delete=models.CASCADE, null=False, db_index=True)
