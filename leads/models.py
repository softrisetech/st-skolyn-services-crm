from django.db import models
from autoslug import AutoSlugField
from core.base_models import BaseBusinessModel
from core.constants.model_constants import CHAR_LENGTH, LONG_CHAR_LENGTH, LONG_TEXT_LENGTH, PHONE_LENGTH, EMAIL_LENGTH, DECIMAL_LENGTH, DECIMAL_PLACES_LENGTH


class Medium(BaseBusinessModel):
    name = models.CharField(max_length=CHAR_LENGTH)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, null=True, unique_with=['business_id'], always_update=True)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'business_id'],
                condition=models.Q(deleted_at__isnull=True),  # only enforce for active rows
                name='unique_slug_per_business'
            )
        ]

class Source(BaseBusinessModel):
    name = models.CharField(max_length=CHAR_LENGTH)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, null=True, unique_with=['business_id'], always_update=True)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'business_id'],
                condition=models.Q(deleted_at__isnull=True),  # only enforce for active rows
                name='unique_slug_per_business_source'
            )
        ]

class Stage(BaseBusinessModel):
    name = models.CharField(max_length=CHAR_LENGTH)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, null=True, unique_with=['business_id'], always_update=True)
    priority = models.PositiveSmallIntegerField()
    is_default = models.BooleanField(default=False)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)
    type = models.CharField(default="open")

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'business_id'],
                condition=models.Q(deleted_at__isnull=True),
                name='unique_slug_business_stage'
            )
        ]

class Tag(BaseBusinessModel):
    name = models.CharField(max_length=CHAR_LENGTH)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, null=True, unique_with=['business_id'], always_update=True)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'business_id'],
                condition=models.Q(deleted_at__isnull=True),  # only enforce for active rows
                name='unique_slug_per_business_tag'
            )
        ]


class Lead(BaseBusinessModel):
    branch_id = models.UUIDField(db_index=True)
    session_id = models.UUIDField(null=True, blank=True, db_index=True)
    medium = models.ForeignKey('Medium', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    source = models.ForeignKey('Source', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    stage = models.ForeignKey('Stage', on_delete=models.CASCADE, db_index=True)
    created_by = models.UUIDField(db_index=True)
    assigned_to = models.UUIDField(null=True, blank=True, db_index=True)
    first_name = models.CharField(max_length=CHAR_LENGTH)
    last_name = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    priority = models.PositiveSmallIntegerField()
    date_of_birth = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=PHONE_LENGTH, null=True, blank=True)
    email = models.EmailField(max_length=EMAIL_LENGTH, null=True, blank=True)
    location = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    previous_education = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    p_name = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    p_contact_number = models.CharField(max_length=PHONE_LENGTH, null=True, blank=True)
    p_email = models.EmailField(max_length=EMAIL_LENGTH, null=True, blank=True)
    registration_no = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    is_imported = models.BooleanField(default=False)
    imported_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        ordering = ['-updated_at']

    def get_medium(self):
        try:
            medium = Medium.objects.get(id=self.medium_id)
            return medium
        except Medium.DoesNotExist:
            return None

    def get_stage(self):
        try:
            stage = Stage.objects.get(id=self.stage_id)
            return stage
        except Stage.DoesNotExist:
            return None

    def get_source(self):
        try:
            source = Source.objects.get(id=self.source_id)
            return source
        except Source.DoesNotExist:
            return None

    def get_tag(self):
        try:
            tag = Tag.objects.get(id=self.tag_id)
            return tag
        except Tag.DoesNotExist:
            return None

    def get_attachments(self):
        attachments = Attachment.objects.filter(lead_id=self.id).values("id", "path")

        # Convert UUIDs to strings
        formatted_attachments = [
            {"id": str(attachment["id"]), "path": attachment["path"]} for attachment in attachments
        ]

        return formatted_attachments if formatted_attachments else None

    def get_registration(self):
        try:
            registration = Registration.objects.filter(lead=self.id).values("id", "date", "amount").first()
            return registration
        except Registration.DoesNotExist:
            return None

class FollowUpType(BaseBusinessModel):
    name = models.CharField(max_length=CHAR_LENGTH)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, null=True, unique_with=['business_id'], always_update=True)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'business_id'],
                condition=models.Q(deleted_at__isnull=True),  # only enforce for active rows
                name='unique_slug_per_business_followup_type'
            )
        ]

class FollowUp(BaseBusinessModel):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, db_index=True)
    type_id = models.ForeignKey('FollowUpType', on_delete=models.CASCADE, db_index=True)
    follow_up_by = models.UUIDField(db_index=True)
    date = models.DateField()
    description = models.TextField(max_length=LONG_CHAR_LENGTH)

    class Meta:
        ordering = ['-updated_at']

    def get_follow_up_type(self):
        return self.type_id if self.type_id else None

class Tracking(BaseBusinessModel):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, db_index=True)
    model_id = models.UUIDField()
    model_type = models.PositiveSmallIntegerField()
    user_id = models.UUIDField()

    class Meta:
        ordering = ['-updated_at']

    def get_medium(self):
        try:
            medium = Medium.objects.get(id=self.model_id)
            return medium
        except Medium.DoesNotExist:
            return None

    def get_stage(self):
        try:
            stage = Stage.objects.get(id=self.model_id)
            return stage
        except Stage.DoesNotExist:
            return None

    def get_source(self):
        try:
            source = Source.objects.get(id=self.model_id)
            return source
        except Source.DoesNotExist:
            return None

    def get_tag(self):
        try:
            tag = Tag.objects.get(id=self.model_id)
            return tag
        except Tag.DoesNotExist:
            return None

class Attachment(BaseBusinessModel):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, db_index=True)
    path = models.TextField(max_length=LONG_CHAR_LENGTH)

class LostReason(BaseBusinessModel):
    name = models.CharField(max_length=CHAR_LENGTH)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, null=True, unique_with=['business_id'], always_update=True)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'business_id'],
                condition=models.Q(deleted_at__isnull=True),  # only enforce for active rows
                name='unique_slug_per_business_lost_reason'
            )
        ]

class StageReason(BaseBusinessModel):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, db_index=True)
    stage = models.ForeignKey('Stage', on_delete=models.CASCADE, db_index=True)
    reason_type = models.ForeignKey('LostReason', on_delete=models.CASCADE, db_index=True)
    reason = models.TextField(max_length=LONG_CHAR_LENGTH)

    class Meta:
        ordering = ['-updated_at']

class Registration(BaseBusinessModel):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, db_index=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=DECIMAL_LENGTH, decimal_places=DECIMAL_PLACES_LENGTH)

    class Meta:
        ordering = ['-updated_at']
