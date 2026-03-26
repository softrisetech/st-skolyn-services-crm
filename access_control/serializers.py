from rest_framework import serializers
from .models import Module, Permission, RolePermission

class PermissionSerializer(serializers.ModelSerializer):
    module_obj = serializers.SerializerMethodField()
    class Meta:
        model = Permission
        fields = ['id', 'module', 'module_obj', 'name', 'description', 'request_method', 'url', 'frontend_url', 'key', 'type', 'sort_order', 'is_active', 'created_at', 'updated_at']

    def validate(self, data):
        errors = {}
        name = data.get('name')
        module = data.get('module')

        if self.instance:
            if Permission.objects.filter(name=name, module=module).exclude(id=self.instance.id).exists():
                errors["name"] = ["The name already exists"]
        else:
            if Permission.objects.filter(name=name, module=module).exists():
                errors["name"] = ["The name already exists"]

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def get_module_obj(self, obj):
        module = obj.get_module()
        if module:
            return {
                "id": module.id,
                "name": module.name,
                "slug": module.slug
            }
        return {}

class ModuleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    class Meta:
        model = Module
        fields = ['id', 'app_id', 'name', 'slug', 'description', 'is_active', 'sort_order', 'permissions', 'created_at', 'updated_at', 'app_slug']

    def validate(self, data):
        errors = {}
        name = data.get('name')
        app_id = data.get('app_id')

        if self.instance:
            if Module.objects.filter(name=name, app_id=app_id).exclude(id=self.instance.id).exists():
                errors["name"] = ["The name already exists"]
        else:
            if Module.objects.filter(name=name, app_id=app_id).exists():
                errors["name"] = ["The name already exists"]

        if errors:
            raise serializers.ValidationError(errors)

        return data


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = ["role_id", "permission"]
