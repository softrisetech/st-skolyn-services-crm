from rest_framework.decorators import api_view
from rest_framework import status
from ..models import Module, RolePermission, Permission
from ..serializers import ModuleSerializer, RolePermissionSerializer
from core.utils.response_utils import success_response, error_response
from core.utils.pagination_utils import CustomPagination
import json

@api_view(['POST'])
def role_permissions(request, pk):
    try:
        data = request.data
        request.page_size = "all"
        business_id = data.get('auth_business_id')
        app_slug = data.get('app_slug')

        # ✅ Order modules by sort_order
        queryset = (
            Module.objects
            .filter(app_slug=app_slug, is_active=True)
            .prefetch_related("permissions")
            .order_by("sort_order", "id")
        )

        # ✅ Assigned permissions set
        assigned_permissions = set(
            RolePermission.objects.filter(
                business_id=business_id,
                role_id=pk
            ).values_list("permission_id", flat=True)
        )

        modified_modules = []

        for module in queryset:
            modified_module = {
                "id": module.id,
                "name": module.name,
                "sort_order": module.sort_order,
                "permissions": []
            }

            # ✅ Order permissions by sort_order
            permissions = module.permissions.filter(is_active=True).order_by("sort_order", "id")

            for permission in permissions:
                permission_dict = {
                    "id": permission.id,
                    "module": permission.module_id,
                    "name": permission.name,
                    "sort_order": permission.sort_order,
                    "checked": permission.id in assigned_permissions
                }
                modified_module["permissions"].append(permission_dict)

            modified_modules.append(modified_module)

        # ✅ Pagination
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(modified_modules, request)

        response_data = paginator.get_paginated_response(paginated_queryset)

        return success_response("record_fetched", status.HTTP_200_OK, response_data)

    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def assign_permission_to_role(request, pk):
    try:
        data = []
        permission_modules = request.data.get('role_permissions', [])
        business_id = request.data.get('auth_business_id')

        if not business_id:
            return error_response('auth_business_id is required', status.HTTP_400_BAD_REQUEST)

        module_ids = []
        for permission_module in permission_modules:
            module_ids.append(permission_module["id"])

        permission_ids = Permission.objects.filter(module_id__in=module_ids).values_list("id")
        RolePermission.objects.filter(role_id=pk, business_id=business_id, permission_id__in=permission_ids).delete()

        for permission_module in permission_modules:
            for permissions in permission_module.values():
                for permission in permissions:
                    if isinstance(permission, dict) and permission.get('checked'):
                        data.append({
                            'role_id': pk,
                            'permission': permission.get('id'),
                            'business_id': business_id
                        })

        if data:
            serializer = RolePermissionSerializer(data=data, many=True)
            if serializer.is_valid():
                serializer.save()
                return success_response('Permissions assigned successfully', status.HTTP_201_CREATED, serializer.data)
            else:
                # ✅ convert errors to string so error_response doesn't get a list
                return error_response(str(serializer.errors), status.HTTP_400_BAD_REQUEST)
        else:
            return success_response('Permissions assigned successfully', status.HTTP_201_CREATED, [])

    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)