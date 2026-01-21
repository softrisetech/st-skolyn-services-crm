from rest_framework.decorators import api_view
from rest_framework import status
from ..models import Module, RolePermission, Permission
from ..serializers import ModuleSerializer, RolePermissionSerializer
from core.utils.response_utils import success_response, error_response
from core.utils.pagination_utils import CustomPagination
import json

@api_view(['GET'])
def role_permissions(request, pk):
    try:
        request.page_size = "all"
        business_id = request.query_params.get('auth_business_id')
        app_slug = request.query_params.get('app_slug')

        # Fetch modules with related permissions
        queryset = Module.objects.filter(app_slug=app_slug, is_active=True).prefetch_related("permissions").all()

        # Get assigned role permissions (IDs only) as a set for fast lookup
        assigned_permissions = set(
            RolePermission.objects.filter(role_id=pk).values_list("permission_id", flat=True)
        )

        # ✅ Add "checked" key to each permission before serialization
        modified_modules = []
        for module in queryset:
            modified_module = {
                "id": module.id,
                "name": module.name,
                "permissions": []
            }

            for permission in module.permissions.filter(is_active=True):
                permission_dict = {
                    "id": permission.id,
                    "module": permission.module_id,
                    "name": permission.name,
                    "checked": permission.id in assigned_permissions  # ✅ Add checked key
                }
                modified_module["permissions"].append(permission_dict)

            modified_modules.append(modified_module)

        # Apply pagination
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(modified_modules, request)  # ✅ Paginate modified data

        response_data = paginator.get_paginated_response(paginated_queryset)

        return success_response("record_fetched", status.HTTP_200_OK, response_data)

    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def assign_permission_to_role(request, pk):
    try:
        data = []
        permission_modules = request.data.get('role_permissions', [])

        module_ids = []
        for permission_module in permission_modules:
            module_ids.append(permission_module["id"])

        permission_ids = Permission.objects.filter(module_id__in=module_ids).values_list("id")
        RolePermission.objects.filter(role_id=pk, permission_id__in=permission_ids).delete()

        for permission_module in permission_modules:
            for permissions in permission_module.values():
                for permission in permissions:
                    if isinstance(permission, dict) and permission.get('checked'):
                        data.append({'role_id': pk, 'permission': permission.get('id')})

        if data:
            serializer = RolePermissionSerializer(data=data, many=True)
            if serializer.is_valid():
                serializer.save()
                return success_response('Permissions assigned successfully', status.HTTP_201_CREATED, serializer.data)
            else:
                return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            return success_response('Permissions assigned successfully', status.HTTP_201_CREATED, [])


    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
