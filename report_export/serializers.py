from django.db import transaction
from rest_framework import serializers
from .models import Export


class ExportSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    link = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    class Meta:
        model = Export
        fields = [
            "id",
            "business_id",
            "app_slug",
            "type",
            "status",
            "created_by",
            "payload",
            "link",
            "file_name",
            "format_type",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = [
            "id",
            "business_id",
            "app_slug",
            "type",
            "created_by",
            "payload",
            "created_at",
            "updated_at",
            "deleted_at",
        ]

    def validate_status(self, value):
        if not value:
            raise serializers.ValidationError("Status is required and cannot be null or empty.")
        return value

    def validate_link(self, value):
        if not value:
            raise serializers.ValidationError("Link cannot be null or empty.")
        return value

    def validate(self, attrs):
        allowed = {"status", "link"}
        for key in attrs.keys():
            if key not in allowed:
                raise serializers.ValidationError({
                    key: "This field cannot be updated."
                })

        return attrs