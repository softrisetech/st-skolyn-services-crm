from rest_framework import serializers
from core.constants.model_constants import STAGE, BRANCH, MEDIUM, TAG, SOURCE
from .models import Lead, FollowUp, LostReason, Medium, Source, Stage, Tag, Tracking, FollowUpType

NAME_ALREADY_EXISTS = "The name already exists"

class LeadSerializer(serializers.ModelSerializer):
    medium_name = serializers.SerializerMethodField()
    source_name = serializers.SerializerMethodField()
    stage_name = serializers.SerializerMethodField()
    tag_name = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    registration = serializers.SerializerMethodField()
    class Meta:
        model = Lead
        fields = ['id', 'business_id', 'branch_id', 'medium', 'medium_name', 'source', 'source_name', 'stage',
                  'stage_name', 'tag', 'tag_name', 'session_id', 'created_by', 'assigned_to', 'priority', 'first_name', 'last_name',
                  'contact_number', 'email', 'location', 'previous_education', 'date_of_birth', 'p_name',
                  'p_contact_number', 'p_email', 'attachments', 'registration', 'registration_no', 'created_at', 'updated_at',
                  'is_imported', 'imported_at']

    def get_medium_name(self, obj):
        medium = obj.get_medium()
        return medium.name if medium else None

    def get_source_name(self, obj):
        source = obj.get_source()
        return source.name if source else None

    def get_stage_name(self, obj):
        stage = obj.get_stage()
        return stage.name if stage else None

    def get_tag_name(self, obj):
        tag = obj.get_tag()
        return tag.name if tag else None

    def get_attachments(self, obj):
        attachments = obj.get_attachments()
        return attachments if attachments else []

    def get_registration(self, obj):
        registration = obj.get_registration()
        return registration if registration else {}


class StageLeadSerializer(serializers.ModelSerializer):
    source_name = serializers.SerializerMethodField()
    registration = serializers.SerializerMethodField()
    class Meta:
        model = Lead
        fields = ['id', 'business_id', 'source_name', 'name', 'previous_education', 'priority', 'session_id', 'branch_id', 'assigned_to', 'registration']

    def get_source_name(self, obj):
        source = obj.get_source()
        return source.name if source else None

    def get_registration(self, obj):
        registration = obj.get_registration()
        return registration if registration else {}


class FollowUpSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format='%Y-%m-%d')
    type_name = serializers.SerializerMethodField()
    class Meta:
        model = FollowUp
        fields = ["id", "business_id", "lead_id", "type_id", "type_name", "follow_up_by", "date", "description", "created_at", "updated_at"]

    def get_type_name(self, obj):
        follow_up_type = obj.get_follow_up_type()
        return follow_up_type.name if follow_up_type else None

class MediumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medium
        fields = ['id', 'business_id', 'name', 'slug', 'description', 'is_active', 'created_at', 'updated_at']

    def validate(self, data):
        errors = {}
        name = data.get('name')
        business_id = data.get('business_id')

        if self.instance:
            if Medium.objects.filter(name=name, business_id=business_id).exclude(id=self.instance.id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]
        else:
            if Medium.objects.filter(name=name, business_id=business_id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]

        if errors:
            raise serializers.ValidationError(errors)

        return data

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'business_id', 'name', 'slug', 'description', 'is_active', 'created_at', 'updated_at']

    def validate(self, data):
        errors = {}
        name = data.get('name')
        business_id = data.get('business_id')
        medium = data.get('medium')

        if self.instance:
            if Source.objects.filter(name=name, business_id=business_id).exclude(id=self.instance.id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]
        else:
            if Source.objects.filter(name=name, business_id=business_id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]

        if errors:
            raise serializers.ValidationError(errors)

        return data

class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id', 'business_id', 'name', 'slug', 'priority', 'type', 'is_default', 'description', 'is_active', 'created_at', 'updated_at']

    def validate(self, data):
        errors = {}
        name = data.get('name')
        business_id = data.get('business_id')
        type = data.get('type')

        if self.instance:
            if Stage.objects.filter(name=name, business_id=business_id).exclude(id=self.instance.id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]
        else:
            if Stage.objects.filter(name=name, business_id=business_id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]

        if errors:
            raise serializers.ValidationError(errors)

        return data

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'business_id', 'name', 'slug', 'description', 'is_active', 'created_at', 'updated_at']

    def validate(self, data):
        errors = {}
        name = data.get('name')
        business_id = data.get('business_id')

        if self.instance:
            if Tag.objects.filter(name=name, business_id=business_id).exclude(id=self.instance.id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]
        else:
            if Tag.objects.filter(name=name, business_id=business_id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]

        if errors:
            raise serializers.ValidationError(errors)

        return data
    
class TrackingSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    name = serializers.SerializerMethodField()
    model_name = serializers.SerializerMethodField()

    class Meta:
        model = Tracking
        fields = [
            'id', 'business_id', 'lead_id', 'model_id', 'model_type', 'model_name', 'name', 'created_at', 'user_id'
        ]

    def get_name(self, obj):
        if obj.model_type == STAGE:
            return obj.get_stage().name
        elif obj.model_type == SOURCE:
            return obj.get_source().name
        elif obj.model_type == MEDIUM:
            return obj.get_medium().name
        elif obj.model_type == TAG:
            return obj.get_tag().name
        else:
            return ""

    def get_model_name(self, obj):
        if obj.model_type == STAGE:
            return "Stage"
        elif obj.model_type == SOURCE:
            return "Source"
        elif obj.model_type == MEDIUM:
            return "Medium"
        elif obj.model_type == TAG:
            return "Tag"
        elif obj.model_type == BRANCH:
            return "Branch"
        else:
            return ""


class LeadImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            'business_id', 'branch_id', 'name', 'email', 'other_info', 'session_id',
            'contact_number', 'medium', 'source', 'tag', 'stage', 'is_opportunity',
            'p_name', 'p_contact_number', 'p_email', 'date_of_birth', 'previous_education',
            'created_by', 'created_at', 'updated_at', 'registration_no', 'priority', 'is_imported', 'imported_at'
        ]

class FollowUpTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpType
        fields = ('id', 'business_id', 'name', 'is_active', 'created_at', 'updated_at')

    def validate(self, data):
        errors = {}
        name = data.get('name')
        business_id = data.get('business_id')

        if self.instance:
            if FollowUpType.objects.filter(name=name,business_id=business_id).exclude(id=self.instance.id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]
        else:
            if FollowUpType.objects.filter(name=name,business_id=business_id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]

        if errors:
            raise serializers.ValidationError(errors)

        return data

class LostReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostReason
        fields = ('id', 'business_id', 'name', 'is_active', 'created_at', 'updated_at')

    def validate(self, data):
        errors = {}
        name = data.get('name')
        business_id = data.get('business_id')

        if self.instance:
            if LostReason.objects.filter(name=name,business_id=business_id).exclude(id=self.instance.id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]
        else:
            if LostReason.objects.filter(name=name,business_id=business_id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]

        if errors:
            raise serializers.ValidationError(errors)

        return data


class LeadExportSerializer(serializers.ModelSerializer):
    medium_name = serializers.SerializerMethodField()
    source_name = serializers.SerializerMethodField()
    stage_name = serializers.SerializerMethodField()
    tag_name = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            'business_id', 'branch_id', 'name', 'email', 'other_info', 'session_id',
            'contact_number', 'medium', 'medium_name', 'source', 'source_name', 'stage', 'stage_name', 'is_opportunity',
            'p_name', 'p_contact_number', 'p_email', 'date_of_birth', 'previous_education',
            'created_by', 'created_at', 'updated_at', 'registration_no', 'priority', 'tag', 'tag_name'
        ]

    def get_medium_name(self, obj):
        medium = obj.get_medium()
        return medium.name if medium else None

    def get_source_name(self, obj):
        source = obj.get_source()
        return source.name if source else None

    def get_tag_name(self, obj):
        tag = obj.get_tag()
        return tag.name if tag else None

    def get_stage_name(self, obj):
        stage = obj.get_stage()
        return stage.name if stage else None