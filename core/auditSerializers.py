from rest_framework import serializers
from core.audit_models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField()
    action = serializers.CharField()
    changes = serializers.JSONField()
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'content_type',
            'object_id',
            'model_name',
            'action',
            'changes',
            'business_id',
            'auth_id',
            'remote_addr',
            'timestamp',
        ]