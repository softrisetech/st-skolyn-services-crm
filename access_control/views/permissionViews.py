from rest_framework.decorators import APIView, api_view
from rest_framework import status
from django.db.models import Q
from ..models import *
from ..serializers import PermissionSerializer
from core.utils.response_utils import success_response, error_response
from core.utils.pagination_utils import CustomPagination
from core.utils.date_time_converter import DateTimeConverter

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

        module = filters.get('module_id')
        if module:
            queryset = queryset.filter(module=module)

        type = filters.get('type')
        if type is not None:
            queryset = queryset.filter(type=type)

        is_active = filters.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

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

@api_view(["GET"])
def get_role_based_permissions(request):
    data = request.query_params
    business_id = data.get("auth_business_id")
    is_staff = data.get("auth_is_staff")
    if is_staff == "true":
        role_id = data.get("auth_role_id")
        role_permission_ids = RolePermission.objects.filter(role_id=role_id).values("permission_id")
        permissions = Permission.objects.filter(id__in=role_permission_ids)
    else:
        permissions = Permission.objects.all()

    permission_data = PermissionSerializer(permissions, many=True).data

    result = {}

    for permission in permission_data:
        module_slug = permission["module_obj"]["slug"]

        url = permission["url"] or ""
        frontend_url = permission["frontend_url"] or ""
        key = permission["key"] or ""

        if module_slug in result:
            if url:
                result[module_slug]["backend_url"].extend([u.strip() for u in url.split(",") if u.strip()])
            if frontend_url:
                result[module_slug]["frontend_url"].extend([u.strip() for u in frontend_url.split(",") if u.strip()])
            if key:
                result[module_slug]["key"].append(key)
        else:
            result[module_slug] = {
                "module_id": permission["module"],
                "backend_url": [u.strip() for u in url.split(",") if u.strip()] if url else [],
                "frontend_url": [u.strip() for u in frontend_url.split(",") if u.strip()] if frontend_url else [],
                "key": [key] if key else []
            }

        #remove duplicates
        for module_data in result.values():
            module_data["backend_url"] = list(set(module_data["backend_url"]))
            module_data["frontend_url"] = list(set(module_data["frontend_url"]))
            module_data["key"] = list(set(module_data["key"]))

    return success_response('record_fetched', status.HTTP_200_OK, result)
