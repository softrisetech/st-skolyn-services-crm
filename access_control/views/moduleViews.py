from rest_framework.decorators import APIView, api_view
from rest_framework import status
from django.db.models import Q
from ..models import Module
from ..serializers import ModuleSerializer, PermissionSerializer
from core.utils.response_utils import success_response, error_response
from core.utils.pagination_utils import CustomPagination
import json
from core.utils.date_time_converter import DateTimeConverter


class ModuleView(APIView):
    pagination_class = CustomPagination

    def get_queryset(self):
        return Module.objects.filter()

    def apply_filters(self, queryset, filters):
        """Apply search and filter conditions to the queryset."""
        search_query = filters.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        app_id = filters.get('app_id')
        if app_id is not None:
            queryset = queryset.filter(app_id=app_id)

        app_slug = filters.get('app_slug')
        if app_slug is not None:
            queryset = queryset.filter(app_slug=app_slug)

        is_active = filters.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        return queryset

    def get(self, request, pk=None):
        timezone = request.query_params.get("auth_timezone")
        queryset = self.get_queryset().prefetch_related('permissions')

        if pk:
            module = queryset.filter(id=pk).first()
            if module:
                serialized_data = ModuleSerializer(module).data
                serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], timezone)
                serialized_data["updated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["updated_at"], timezone)
                return success_response('record_fetched', status.HTTP_200_OK, serialized_data)

            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

        # Apply filters and pagination for list view
        filters = request.query_params
        queryset = self.apply_filters(queryset, filters)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serialized_data = ModuleSerializer(paginated_queryset, many=True).data
        for data in serialized_data:
            data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
            data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)

        response_data = paginator.get_paginated_response(serialized_data)
        return success_response('record_fetched', status.HTTP_200_OK, response_data)

    def post(self, request):
        try:
            app_id = request.data.get("app_id")
            app_slug = request.data.get("app_slug")
            modules = request.data.get("modules", [])

            # Append app_id to each module
            for module in modules:
                module["app_id"] = app_id
                module["app_slug"] = app_slug

            serializer = ModuleSerializer(data=modules, many=True)
            if serializer.is_valid():
                serializer.save()
                return success_response('record_stored', status.HTTP_201_CREATED, serializer.data)

            return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

        except Exception as e:
            return error_response('server_error', status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

    def put(self, request, pk=None):
        try:
            module = Module.objects.get(id=pk)
        except Module.DoesNotExist:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

        data = request.data
        serializer = ModuleSerializer(instance=module, data=data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return success_response('record_updated', status.HTTP_200_OK, serializer.data)
        return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    def delete(self, request, pk=None):
        try:
            module = Module.objects.get(id=pk)
            module.delete()
            return success_response('record_deleted', status.HTTP_200_OK)
        except Module.DoesNotExist:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
def change_module_status(request, pk=None):
    try:
        module = Module.objects.get(id=pk)
    except Module.DoesNotExist:
        return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

    data = request.data
    serializer = ModuleSerializer(instance=module, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return success_response('record_updated', status.HTTP_200_OK, serializer.data)
    return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

