from rest_framework import serializers
from core.constants.model_constants import STAGE, TEAM, MEDIUM, TAG, SOURCE, CAMPAIGN
from .models import PreRequisite, PreRequisiteCourse, Institute, Attachment, Lead, FollowUp, Medium, Source, Stage, StageReason, Tag, Campaign, Tracking, FollowUpType, Team, TeamMember, Contact, SessionTarget, QuickEmail

NAME_ALREADY_EXISTS = "The name already exists"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            "id", "business_id", "father_first_name", "father_last_name", "father_contact_number", "father_email", "father_nic", "is_father_applicable",
            "mother_first_name", "mother_last_name", "mother_contact_number", "mother_email", "mother_nic", "is_mother_applicable", "created_at", "updated_at"
        ]

    def validate(self, data):
        errors = {}

        business_id = data.get('business_id') or (self.instance.business_id if self.instance else None)

        father_nic = data.get('father_nic')
        mother_nic = data.get('mother_nic')

        queryset = Contact.objects.filter(business_id=business_id)

        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        if father_nic and queryset.filter(father_nic=father_nic).exists():
            errors["father_nic"] = "This father NIC already exists."

        if mother_nic and queryset.filter(mother_nic=mother_nic).exists():
            errors["mother_nic"] = "This mother NIC already exists."

        if father_nic and mother_nic and father_nic == mother_nic:
            errors["father_nic"] = ["Father NIC and Mother NIC cannot be the same."]

        if errors:
            raise serializers.ValidationError(errors)

        return data

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'business_id', 'lead', 'file']

class LeadListSerializer(serializers.ModelSerializer):
    medium_name = serializers.CharField(source="medium.name", read_only=True)
    source_name = serializers.CharField(source="source.name", read_only=True)
    stage_name = serializers.CharField(source="stage.name", read_only=True)
    tag_name = serializers.CharField(source="tag.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    contact = ContactSerializer(read_only=True)
    class Meta:
        model = Lead
        fields = [
                    "id", "business_id", "branch_id", "session_id", "class_id", "medium", "medium_name", "source", "source_name", "stage", "stage_name", "tag", "tag_name", "team", "team_name", "campaign", "campaign_name", "contact", "code", "created_by", "assigned_to", "country_id",
                    "state_id", "city_id", "first_name", "last_name", "priority", "date_of_birth", "contact_number",
                    "email", "nic", "gender", "ethnicity", "remarks", "is_imported", "imported_at", "created_at", "updated_at"
                ]
        
class LeadGetSerializer(serializers.ModelSerializer):
    medium_name = serializers.CharField(source="medium.name", read_only=True)
    source_name = serializers.CharField(source="source.name", read_only=True)
    stage_name = serializers.CharField(source="stage.name", read_only=True)
    tag_name = serializers.CharField(source="tag.name", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    contact = ContactSerializer(read_only=True)
    attachments = serializers.SerializerMethodField()
    class Meta:
        model = Lead
        fields = [
                    "id", "business_id", "branch_id", "session_id", "class_id", "medium", "medium_name", "source", "source_name", "stage", "stage_name", "tag", "tag_name", "team", "team_name", "campaign", "campaign_name", "contact", "code", "created_by", "assigned_to", "country_id",
                    "state_id", "city_id", "first_name", "last_name", "priority", "date_of_birth", "contact_number",
                    "email", "nic", "gender", "ethnicity", "remarks", "is_imported", "imported_at", "created_at", "updated_at", "attachments"
                ]
        
    def get_attachments(self, obj):
        attachments = obj.get_attachments()
        return attachments if attachments else []
        
class LeadStoreSerializer(serializers.ModelSerializer):
    parent_contact = ContactSerializer(source="contact", read_only=True)
    class Meta:
        model = Lead
        fields = [
                    "id", "business_id", "branch_id", "session_id", "class_id", "medium", "source", "stage", "tag", "team", "campaign", "parent_contact", "contact", "code", "created_by", "assigned_to", "country_id",
                    "state_id", "city_id", "first_name", "last_name", "priority", "date_of_birth", "contact_number",
                    "email", "nic", "gender", "ethnicity", "remarks", "is_imported", "imported_at", "created_at", "updated_at"
                ]



class KanbanLeadSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.name", read_only=True)
    class Meta:
        model = Lead
        fields = ['id', 'business_id', 'source_name', 'first_name', 'last_name', 'priority', 'session_id', 'branch_id', 'assigned_to']


class FollowUpSerializer(serializers.ModelSerializer):
    date_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    follow_type_name = serializers.CharField(source="follow_up_type.name", read_only=True)
    class Meta:
        model = FollowUp
        fields = ["id", "business_id", "lead", "follow_up_type", "follow_type_name", "created_by", "date_time", "description", "is_done", "created_at", "updated_at"]

class PreRequisiteCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreRequisiteCourse
        fields = ['id', 'business_id', 'lead', 'prerequisite', 'course_name', 'max_marks', 'passing_marks', 'marks_in_percentage', 'is_mandatory']

class PreRequisiteSerializer(serializers.ModelSerializer):
    courses = PreRequisiteCourseSerializer(many=True, read_only=True)
    institute_name = serializers.CharField(source="institute.name", read_only=True)
    class Meta:
        model = PreRequisite
        fields = ["id", "business_id", "lead", "institute", "institute_name", "board_name", "code", "program", "courses", "created_at", "updated_at"]


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

        if self.instance:
            if Stage.objects.filter(name=name, business_id=business_id).exclude(id=self.instance.id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]
        else:
            if Stage.objects.filter(name=name, business_id=business_id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]

        if errors:
            raise serializers.ValidationError(errors)

        return data
    
class StageReasonSerializer(serializers.ModelSerializer):
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    class Meta:
        model = StageReason
        fields = ['id', 'business_id', 'stage', 'stage_name', 'name', 'slug', 'description', 'is_active', 'created_at', 'updated_at']

    def validate(self, data):
        errors = {}
        name = data.get('name')
        stage = data.get('stage')
        business_id = data.get('business_id')

        if self.instance:
            if StageReason.objects.filter(name=name, stage=stage, business_id=business_id).exclude(id=self.instance.id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]
        else:
            if StageReason.objects.filter(name=name, stage=stage, business_id=business_id).exists():
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
    

class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = ['id', 'business_id', 'name', 'is_active', 'created_at', 'updated_at']

    def validate(self, data):
        errors = {}
        name = data.get('name')
        business_id = data.get('business_id')

        if self.instance:
            if Institute.objects.filter(name=name, business_id=business_id).exclude(id=self.instance.id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]
        else:
            if Institute.objects.filter(name=name, business_id=business_id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]

        if errors:
            raise serializers.ValidationError(errors)

        return data


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['id', 'business_id', 'name', 'slug', 'description', 'is_active', 'created_at', 'updated_at']

    def validate(self, data):
        errors = {}
        name = data.get('name')
        business_id = data.get('business_id')

        if self.instance:
            if Campaign.objects.filter(name=name, business_id=business_id).exclude(id=self.instance.id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]
        else:
            if Campaign.objects.filter(name=name, business_id=business_id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]

        if errors:
            raise serializers.ValidationError(errors)

        return data
    

class DashboardCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['id', 'name', 'is_active', 'created_at', 'updated_at']
    
    
class TrackingSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    name = serializers.SerializerMethodField()

    class Meta:
        model = Tracking
        fields = [
            'id', 'business_id', 'lead_id', 'model_id', 'model_type', 'name', 'created_at', 'user_id'
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
        elif obj.model_type == TEAM:
            return obj.get_team().name
        elif obj.model_type == CAMPAIGN:
            return obj.get_campaign().name
        else:
            return ""


class LeadImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = [
            'business_id', 'branch_id', 'medium', 'source', 'stage', 'tag', 'first_name', 'last_name', 
            'date_of_birth', 'contact_number', 'email', 'nic', 'gender', 'remarks', 'created_at', 'updated_at',
            'created_by', 'priority', 'is_imported', 'imported_at'    
        ]

class FollowUpTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpType
        fields = ('id', 'business_id', 'name', 'slug', 'is_active', 'description', 'integrate_with_google_calendar', 'created_at', 'updated_at')

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

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ['user_id']


class TeamSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    class Meta:
        model = Team
        fields = ('id', 'business_id', 'branch_id', 'user_id', 'name', 'description', 'is_active', 'members', 'created_at', 'updated_at')

    def validate(self, data):
        errors = {}
        name = data.get('name')
        business_id = data.get('business_id')

        if self.instance:
            if Team.objects.filter(name=name,business_id=business_id).exclude(id=self.instance.id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]
        else:
            if Team.objects.filter(name=name,business_id=business_id).exists():
                errors["name"] = [NAME_ALREADY_EXISTS]

        if errors:
            raise serializers.ValidationError(errors)

        return data
    
    def get_members(self, obj):
        return list(
            obj.members.values_list('user_id', flat=True)
        )


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
    

class SessionTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionTarget
        fields = ['id', 'business_id', 'branch_id', 'session_id', 'target', 'created_at', 'updated_at']

    def validate(self, data):
        errors = {}
        branch_id = data.get('branch_id')
        session_id = data.get('session_id')
        business_id = data.get('business_id')

        if self.instance:
            if SessionTarget.objects.filter(branch_id=branch_id, session_id=session_id, business_id=business_id).exclude(id=self.instance.id).exists():
                errors["branch_id"] = ["Targets are already defined for this branch and session"]
        else:
            if SessionTarget.objects.filter(branch_id=branch_id, session_id=session_id, business_id=business_id).exists():
                errors["branch_id"] = ["Targets are already defined for this branch and session"]

        if errors:
            raise serializers.ValidationError(errors)

        return data
    
class LeadQuickEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickEmail
        fields = ["id", "business_id", "recipients", "subject", "message", "created_at", "updated_at"]