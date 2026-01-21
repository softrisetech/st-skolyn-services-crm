import uuid
from django.db import models
from django.utils.timezone import now

class SoftDeleteManager(models.Manager):
    """
    Custom manager to exclude soft-deleted records by default.
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def restore_all(self):
        """
        Restore all soft-deleted records.
        """
        return super().get_queryset().filter(deleted_at__isnull=False).update(deleted_at=None)


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)


    # Managers
    objects = SoftDeleteManager()  # Default manager to exclude soft-deleted records
    all_objects = models.Manager()  # Includes soft-deleted records

    def delete(self, using=None, keep_parents=False):
        """
        Override the delete method to perform a soft delete.
        """
        self.deleted_at = now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        """
        Permanently delete the record from the database.
        """
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """
        Restore a soft-deleted record.
        """
        self.deleted_at = None
        self.save()

    def is_deleted(self):
        """
        Check if the record is soft-deleted.
        """
        return self.deleted_at is not None

    class Meta:
        abstract = True

class BaseBusinessModel(BaseModel):
    business_id = models.UUIDField(editable=True, db_index=True, null=True, blank=True)

    class Meta:
        abstract = True
