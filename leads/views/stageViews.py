from django.db.models import Q
from ..models import Stage, Lead
from rest_framework import status
from ..serializers import StageSerializer
from django.utils.decorators import method_decorator
from rest_framework.decorators import APIView, api_view
from core.utils.pagination_utils import CustomPagination
from core.utils.helpers import has_active_child_references
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from django.db import IntegrityError, DatabaseError, transaction
from core.utils.response_utils import success_response, error_response
from core.constants.model_constants import OPEN, WON, LOST, REGISTRATION
from ..utils.filters import filter_by_active, filter_by_default, filter_by_type, filter_by_priority


class StageView(APIView):
    pagination_class = CustomPagination

    def get_queryset(self, business_id):
        """Retrieve the base queryset filtered by business_id."""
        return Stage.objects.filter(business_id=business_id)

    def apply_filters(self, queryset, filters):
        """Apply search and filter conditions to the queryset."""
        search_query = filters.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(type__icontains=search_query)
            )

        queryset = filter_by_type(queryset, filters)
        queryset = filter_by_priority(queryset, filters)
        queryset = filter_by_default(queryset, filters)
        queryset = filter_by_active(queryset, filters)
        return queryset

    @method_decorator(access_control_middleware)
    def get(self, request, pk=None):
        data = request.query_params
        timezone = data.get("auth_timezone")
        auth_business_id = data.get('auth_business_id')
        queryset = self.get_queryset(auth_business_id)

        if pk:
            stage = queryset.filter(id=pk).first()
            if stage:
                serialized_data = StageSerializer(stage).data
                serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], timezone)
                serialized_data["updated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["updated_at"], timezone)
                return success_response('record_fetched', status.HTTP_200_OK, serialized_data)
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)


        # List view with pagination and filters
        filters = request.query_params
        queryset = self.apply_filters(queryset, filters)
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serialized_data = StageSerializer(paginated_queryset, many=True).data
        for data in serialized_data:
            data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
            data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)
        response_data = paginator.get_paginated_response(serialized_data)
        return success_response('record_fetched', status.HTTP_200_OK, response_data)

    @method_decorator(access_control_middleware)
    def post(self, request):
        data = request.data.copy()
        business_id = data.get('auth_business_id')
        data['business_id'] = business_id
        is_default = str(data.get('is_default')).lower() in ("true", "1")

        #check if stage is set as default and status is lost, won or registration
        if is_default:
            if data['status'] in {LOST, WON, REGISTRATION}:
                return error_response('default_stage_not_allowed', status.HTTP_422_UNPROCESSABLE_ENTITY)
            Stage.objects.filter(business_id=business_id, is_default=True).update(is_default=False)

        if data['status'] in {LOST, WON, REGISTRATION}:
            stage_exists = Stage.objects.filter(business_id=business_id, status=data['status']).exists()
            if stage_exists:
                return error_response('predefined_stage_exists', status.HTTP_422_UNPROCESSABLE_ENTITY)

        total_stages = Stage.objects.filter(business_id=business_id).count()
        if total_stages >= 10:
            return error_response('max_stage_limit_reached', status.HTTP_422_UNPROCESSABLE_ENTITY)

        serializer = StageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return success_response('record_stored', status.HTTP_201_CREATED, serializer.data)
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    @method_decorator(access_control_middleware)
    def put(self, request, pk=None):
        data = request.data.copy()
        business_id = data.get('auth_business_id')
        try:
            stage = Stage.objects.get(id=pk, business_id=business_id)
        except Stage.DoesNotExist:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

        data['business_id'] = business_id
        is_default = str(request.data.get('is_default')).lower() in ("true", "1")

        if stage.status in [WON, LOST, REGISTRATION] and data["status"] not in [WON, LOST, REGISTRATION]:
            return error_response('cannot_update_predefined_stages', status.HTTP_422_UNPROCESSABLE_ENTITY)

        if data['status'] in {LOST, WON, REGISTRATION}:
            stage_exists = Stage.objects.filter(business_id=business_id, status=data['status']).exclude(id=pk).exists()
            if stage_exists:
                return error_response('predefined_stage_exists', status.HTTP_422_UNPROCESSABLE_ENTITY)

        if is_default:
            if data['status'] in {LOST, WON, REGISTRATION}:
                return error_response('default_stage_not_allowed', status.HTTP_422_UNPROCESSABLE_ENTITY)
            Stage.objects.filter(business_id=business_id, is_default=True).update(is_default=False)

        serializer = StageSerializer(instance=stage, data=data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return success_response('record_updated', status.HTTP_200_OK, serializer.data)
        return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    @method_decorator(access_control_middleware)
    def delete(self, request, pk=None):
        business_id = request.data.get('auth_business_id')
        try:
            stage = Stage.objects.get(id=pk, business_id=business_id)
            if stage.status in {LOST, WON, REGISTRATION}:
                return error_response('predefined_stage_delete_not_allowed', status.HTTP_422_UNPROCESSABLE_ENTITY)

            if stage.status == OPEN:
                lead_open_stages_count = Stage.objects.filter(business_id=business_id, status=OPEN).count()
                if lead_open_stages_count == 1:
                    return error_response('open_stage_delete_not_allowed', status.HTTP_422_UNPROCESSABLE_ENTITY)

            child_references = [
                {'model': Lead, 'foreign_key': 'stage_id'}
            ]
            has_refs = has_active_child_references(child_references, pk, business_id)
            if has_refs:
                return error_response("related_record_delete_failed", status.HTTP_400_BAD_REQUEST)

            stage.delete()
            return success_response('record_deleted', status.HTTP_200_OK)
        except Stage.DoesNotExist:
            return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@access_control_middleware
def change_stage_status(request, pk=None):
    data = request.data.copy()
    business_id = data.get('auth_business_id')

    try:
        stage = Stage.objects.get(id=pk, business_id=business_id)
    except Stage.DoesNotExist:
        return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

    data['business_id'] = business_id
    serializer = StageSerializer(instance=stage, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return success_response('record_updated', status.HTTP_200_OK, serializer.data)
    return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

@api_view(['POST'])
def create_default_stages(request):
    try:
        business_id = request.data.get('auth_business_id')

        if not business_id:
            return error_response("Business ID is required", status.HTTP_400_BAD_REQUEST)

        # Define default stages
        default_stages = [
            Stage(name="Initial", priority=1, status=OPEN, is_default=True, is_active=True, business_id=business_id),
            Stage(name="Won", priority=2, status=WON, is_default=False, is_active=True, business_id=business_id),
            Stage(name="Lost", priority=3, status=LOST, is_default=False, is_active=True, business_id=business_id),
            Stage(name="Registration", priority=3, status=REGISTRATION, is_default=False, is_active=True, business_id=business_id)
        ]

        # Bulk insert stages with transaction handling
        with transaction.atomic():
            Stage.objects.bulk_create(default_stages)

        return success_response('record_stored', status.HTTP_201_CREATED)

    except IntegrityError:
        return error_response("Database integrity error occurred", status.HTTP_400_BAD_REQUEST)

    except DatabaseError:
        return error_response("Database error occurred", status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return error_response(f"An unexpected error occurred: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
