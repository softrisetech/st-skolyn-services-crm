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

class StageReason(BaseBusinessModel):
    stage = models.ForeignKey('Stage', on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=CHAR_LENGTH, db_index=True)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, null=True, unique_with=['business_id'], always_update=True)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'business_id'],
                condition=models.Q(deleted_at__isnull=True),  # only enforce for active rows
                name='unique_slug_per_business_stage_reason'
            )
        ]


class Campaign(BaseBusinessModel):
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
                name='unique_slug_per_business_campaign'
             )
         ]


class FollowUpType(BaseBusinessModel):
    name = models.CharField(max_length=CHAR_LENGTH)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True, null=True, unique_with=['business_id'], always_update=True)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)
    integrate_with_google_calendar = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['slug', 'business_id'],
                condition=models.Q(deleted_at__isnull=True),  # only enforce for active rows
                name='unique_slug_per_business_followup_type'
            )
        ]


class Team(BaseBusinessModel):
    user_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=CHAR_LENGTH)
    description = models.TextField(max_length=LONG_CHAR_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']


class TeamMember(BaseBusinessModel):
    team = models.ForeignKey('Team', on_delete=models.CASCADE, db_index=True, related_name='members')
    user_id = models.UUIDField(db_index=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ('team', 'user_id')


class Contact(BaseBusinessModel):
    father_first_name = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    father_last_name = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    father_contact_number = models.CharField(max_length=PHONE_LENGTH, null=True, blank=True)
    father_email = models.EmailField(max_length=EMAIL_LENGTH, null=True, blank=True)
    father_nic = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    mother_first_name = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    mother_last_name = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    mother_contact_number = models.CharField(max_length=PHONE_LENGTH, null=True, blank=True)
    mother_email = models.EmailField(max_length=EMAIL_LENGTH, null=True, blank=True)
    mother_nic = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    is_father_applicable = models.BooleanField(default=True)
    is_mother_applicable = models.BooleanField(default=True)


class Lead(BaseBusinessModel):
    branch_id = models.UUIDField(db_index=True)
    session_id = models.UUIDField(null=True, blank=True, db_index=True)
    class_id = models.UUIDField(null=True, blank=True, db_index=True)
    medium = models.ForeignKey('Medium', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    source = models.ForeignKey('Source', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    stage = models.ForeignKey('Stage', on_delete=models.CASCADE, db_index=True)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    campaign = models.ForeignKey('Campaign', on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    code = models.CharField(max_length=CHAR_LENGTH)
    created_by = models.UUIDField(db_index=True, null=True, blank=True)
    assigned_to = models.UUIDField(null=True, blank=True, db_index=True)
    country_id = models.UUIDField(null=True, blank=True, db_index=True)
    state_id = models.UUIDField(null=True, blank=True, db_index=True)
    city_id = models.UUIDField(null=True, blank=True, db_index=True)
    first_name = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    last_name = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    priority = models.PositiveSmallIntegerField(default=1)
    date_of_birth = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=PHONE_LENGTH, null=True, blank=True)
    email = models.EmailField(max_length=EMAIL_LENGTH, null=True, blank=True)
    nic = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    gender = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    ethnicity = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    remarks = models.TextField(max_length=LONG_TEXT_LENGTH, null=True, blank=True)
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
        attachments = Attachment.objects.filter(lead_id=self.id)

        if not attachments.exists():
            return None

        processed_files = []
        for att in attachments:
            file_obj = att.file  # access the file JSONField or dict
            if file_obj:
                processed_files.append(file_obj)

        return processed_files
    


class Tracking(BaseBusinessModel):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, db_index=True, related_name='trackings')
    model_id = models.UUIDField()
    model_type = models.CharField(max_length=CHAR_LENGTH)
    user_id = models.UUIDField(db_index=True)

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
        
    def get_team(self):
        try:
            team = Team.objects.get(id=self.model_id)
            return team
        except Team.DoesNotExist:
            return None
        
    def get_campaign(self):
        try:
            campaign = Campaign.objects.get(id=self.model_id)
            return campaign
        except Campaign.DoesNotExist:
            return None


class FollowUp(BaseBusinessModel):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, db_index=True)
    follow_up_type = models.ForeignKey('FollowUpType', on_delete=models.CASCADE, db_index=True, null=True, blank=True, related_name='follow_up_type')
    created_by = models.UUIDField(db_index=True)
    date_time = models.DateTimeField()
    description = models.TextField(max_length=LONG_CHAR_LENGTH, null=True, blank=True)
    is_done = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated_at']


class StageReasonEntry(BaseBusinessModel):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, db_index=True)
    stage = models.ForeignKey('Stage', on_delete=models.CASCADE, db_index=True)
    stage_reason = models.ForeignKey('StageReason', on_delete=models.CASCADE, db_index=True)
    remarks = models.TextField(max_length=LONG_CHAR_LENGTH, null=True, blank=True)
    created_by = models.UUIDField(db_index=True)

    class Meta:
        ordering = ['-updated_at']


class Attachment(BaseBusinessModel):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, db_index=True, related_name='attachments')
    file = models.JSONField(max_length=LONG_CHAR_LENGTH)


class Institute(BaseBusinessModel):
    name = models.CharField(max_length=CHAR_LENGTH)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

class PreRequisite(BaseBusinessModel):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, db_index=True, null=True, blank=True)
    institute = models.ForeignKey('Institute', on_delete=models.CASCADE, db_index=True, null=True, blank=True)
    board_name = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    code = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    program = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    

class PreRequisiteCourse(BaseBusinessModel):
    prerequisite = models.ForeignKey('PreRequisite', on_delete=models.CASCADE, db_index=True, related_name='courses')
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, db_index=True)
    course_name = models.CharField(max_length=CHAR_LENGTH, null=True, blank=True)
    max_marks = models.IntegerField()
    passing_marks = models.IntegerField()
    marks_in_percentage = models.BooleanField()
    is_mandatory = models.BooleanField()