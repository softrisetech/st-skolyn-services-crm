from django.db.models import Q
from rest_framework import status
from collections import defaultdict
from ..serializers import PermissionSerializer
from ..models import Permission, RolePermission
from rest_framework.decorators import APIView, api_view
from core.utils.pagination_utils import CustomPagination
from core.utils.date_time_converter import DateTimeConverter
from core.utils.response_utils import success_response, error_response
from ..utils.filters import filter_by_module, filter_by_type, filter_by_active

class PermissionView(APIView):
    pagination_class = CustomPagination

    def get_queryset(self):
        return Permission.objects.filter()

    def apply_filters(self, queryset, filters):
        """Apply search and filter conditions to the queryset."""
        search_query = filters.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(url__icontains=search_query) |
                Q(key__icontains=search_query)
            )

        queryset = filter_by_module(queryset, filters)
        queryset = filter_by_type(queryset, filters)
        queryset = filter_by_active(queryset, filters)
        return queryset

    def get(self, request, pk=None):
        timezone = request.query_params.get("auth_timezone")
        queryset = self.get_queryset()

        if pk:
            permission = queryset.filter(id=pk, module=request.query_params.get('module_id')).first()
            if permission:
                serialized_data = PermissionSerializer(permission).data
                serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], timezone)
                serialized_data["updated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["updated_at"], timezone)
                return success_response('record_fetched', status.HTTP_200_OK, serialized_data)

            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

        # List view with pagination and filters
        filters = request.query_params
        queryset = self.apply_filters(queryset, filters)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serialized_data = PermissionSerializer(paginated_queryset, many=True).data
        for data in serialized_data:
            data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
            data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)

        response_data = paginator.get_paginated_response(serialized_data)
        return success_response('record_fetched', status.HTTP_200_OK, response_data)

    def post(self, request):
        try:
            module_id = request.data.get("module_id")
            permissions = request.data.get("permissions", [])

            # Append module_id to each module
            for permission in permissions:
                permission["module"] = module_id

            serializer = PermissionSerializer(data=permissions, many=True)
            if serializer.is_valid():
                serializer.save()
                return success_response('record_stored', status.HTTP_201_CREATED, serializer.data)

            return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

        except Exception as e:
            return error_response('server_error', status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

    def put(self, request, pk=None):
        try:
            permission = Permission.objects.get(id=pk, module=request.data.get("module_id"))
        except Permission.DoesNotExist:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['module'] = request.data.get("module_id")
        serializer = PermissionSerializer(instance=permission, data=data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return success_response('record_updated', status.HTTP_200_OK, serializer.data)
        return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    def delete(self, request, pk=None):
        try:
            permission = Permission.objects.get(id=pk, module=request.data.get("module_id"))
            permission.delete()
            return success_response('record_deleted', status.HTTP_200_OK)
        except Permission.DoesNotExist:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
def change_permission_status(request, pk=None):
    try:
        permission = Permission.objects.get(id=pk, module=request.data.get("module_id"))
    except Permission.DoesNotExist:
        return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

    data = request.data
    serializer = PermissionSerializer(instance=permission, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return success_response('record_updated', status.HTTP_200_OK, serializer.data)
    return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)


def _split_values(value):
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]

@api_view(["GET"])
def get_role_based_permissions(request):
    data = request.query_params
    is_staff = data.get("auth_is_staff") == "true"

    permissions = Permission.objects.all().select_related("module")

    if is_staff:
        role_id = data.get("auth_role_id")
        permission_ids = RolePermission.objects.filter(
            role_id=role_id
        ).values_list("permission_id", flat=True)
        permissions = permissions.filter(id__in=permission_ids)

    serialized_permissions = PermissionSerializer(permissions, many=True).data

    result = defaultdict(lambda: {
        "module_id": None,
        "backend_url": set(),
        "frontend_url": set(),
        "key": set(),
    })

    for permission in serialized_permissions:
        module_slug = permission["module_obj"]["slug"]
        module_data = result[module_slug]

        module_data["module_id"] = permission["module"]
        module_data["backend_url"].update(_split_values(permission.get("url")))
        module_data["frontend_url"].update(_split_values(permission.get("frontend_url")))

        key = permission.get("key")
        if key:
            module_data["key"].add(key)

    final_result = {
        slug: {
            "module_id": data["module_id"],
            "backend_url": list(data["backend_url"]),
            "frontend_url": list(data["frontend_url"]),
            "key": list(data["key"]),
        }
        for slug, data in result.items()
    }

    return success_response(
        "record_fetched",
        status.HTTP_200_OK,
        final_result
    )

