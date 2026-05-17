from django.db.models import Q
from ..models import Stage, Lead, StageReasonEntry
from rest_framework import status
from ..serializers import StageSerializer
from rest_framework.decorators import api_view
from core.utils.pagination_utils import CustomPagination
from core.utils.helpers import has_active_child_references
from core.constants.model_constants import OPEN, WON, LOST
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from django.db import IntegrityError, DatabaseError, transaction
from core.utils.response_utils import success_response, error_response
from ..utils.filters import filter_by_active, filter_by_default, filter_by_type, filter_by_priorities, filter_by_sort_order


def __queryset(business_id):
    return Stage.objects.filter(business_id=business_id)


def __apply_filters(queryset, filters):
    search_query = filters.get('search')
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(type__icontains=search_query)
        )

    queryset = filter_by_type(queryset, filters)
    queryset = filter_by_priorities(queryset, filters)
    queryset = filter_by_default(queryset, filters)
    queryset = filter_by_active(queryset, filters)
    queryset = filter_by_sort_order(queryset, filters)
    return queryset


@api_view(['POST'])
@access_control_middleware
def get_lead_stages(request):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')
    queryset = __queryset(business_id)
    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = StageSerializer(paginated_queryset, many=True).data
    for data in serialized_data:
        data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
        data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)
    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)


@api_view(['POST'])
@access_control_middleware
def get_lead_stage(request, pk=None):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')
    stage = __queryset(business_id).filter(id=pk).first()
    if not stage:
        return error_response('stage_not_found', status.HTTP_404_NOT_FOUND)

    serialized_data = StageSerializer(stage).data
    serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], timezone)
    serialized_data["updated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["updated_at"], timezone)
    return success_response('record_fetched', status.HTTP_200_OK, serialized_data)


@api_view(['POST'])
@access_control_middleware
def store_lead_stage(request):
    data = request.data.copy()
    business_id = data.get('auth_business_id')
    data['business_id'] = business_id
    is_default = data.get('is_default')

    #check if stage is set as default and type is lost, won
    if is_default:
        Stage.objects.filter(business_id=business_id, is_default=True).update(is_default=False)

    if data["type"] in [WON, LOST]:
        return error_response('you_cannot_create_these_stage_types', status.HTTP_422_UNPROCESSABLE_ENTITY)

    total_stages = Stage.objects.filter(business_id=business_id).count()
    if total_stages >= 10:
        return error_response('max_stage_limit_reached', status.HTTP_422_UNPROCESSABLE_ENTITY)

    serializer = StageSerializer(data=data)
    if not serializer.is_valid():
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    serializer.save()
    return success_response('record_stored', status.HTTP_201_CREATED, serializer.data)


@api_view(['POST'])
@access_control_middleware
def update_lead_stage(request, pk=None):
    data = request.data.copy()
    business_id = data.get('auth_business_id')
    stage = __queryset(business_id).filter(id=pk).first()
    if not stage:
        return error_response('stage_not_found', status.HTTP_404_NOT_FOUND)

    data['business_id'] = business_id
    is_default = data.get('is_default')

    if data["type"] in [WON, LOST]:
        return error_response('you_cannot_create_these_stage_types', status.HTTP_422_UNPROCESSABLE_ENTITY)

    is_last_stage = check_if_stage_is_last_of_its_type(stage)
    new_type = data.get("type")
    is_active = data.get("is_active")

    # normalize is_active once
    is_deactivating = str(is_active).lower() in ["0", "false"]

    if is_last_stage:
        if stage.type != new_type:
            return error_response(
                'last_stage_updation_not_allowed',
                status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        if is_deactivating:
            return error_response(
                'last_stage_inactive_not_allowed',
                status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    if is_default:
        if data["type"] in [WON, LOST]:
            return error_response('you_cannot_set_default_these_stage_types', status.HTTP_422_UNPROCESSABLE_ENTITY)

        Stage.objects.filter(business_id=business_id, is_default=True).update(is_default=False)
    else:
        stage_default_exists = Stage.objects.filter(business_id=business_id, is_default=True).exists()
        if not stage_default_exists:
            return error_response('atleast_one_stage_should_be_default', status.HTTP_422_UNPROCESSABLE_ENTITY)

    serializer = StageSerializer(instance=stage, data=data, partial=False)
    if not serializer.is_valid():
        return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    serializer.save()
    return success_response('record_updated', status.HTTP_200_OK, serializer.data)


@api_view(['POST'])
@access_control_middleware
def delete_lead_stage(request, pk=None):
    business_id = request.data.get('auth_business_id')
    stage = __queryset(business_id).filter(id=pk).first()
    if not stage:
        return error_response('stage_not_found', status.HTTP_404_NOT_FOUND)

    if check_if_stage_is_last_of_its_type(stage):
        return error_response('last_stage_deletion_not_allowed', status.HTTP_422_UNPROCESSABLE_ENTITY)

    child_references = [
        {'model': Lead, 'foreign_key': 'stage_id'},
        {'model': StageReasonEntry, 'foreign_key': 'stage_id'}
    ]
    has_refs = has_active_child_references(child_references, pk, business_id)
    if has_refs:
        return error_response("related_stage_record_found_on_deletion", status.HTTP_422_UNPROCESSABLE_ENTITY)

    stage.delete()
    return success_response('record_deleted', status.HTTP_200_OK)


def check_if_stage_is_last_of_its_type(stage):
    stages_count = Stage.objects.filter(business_id=stage.business_id, type=stage.type).count()
    return stages_count == 1


@api_view(['POST'])
def create_default_stages(request):
    try:
        business_id = request.data.get('auth_business_id')

        if not business_id:
            return error_response("Business ID is required", status.HTTP_400_BAD_REQUEST)

        # Define default stages
        default_stages = [
            Stage(name="Initial", priority=1, type=OPEN, is_default=True, is_active=True, business_id=business_id),
            Stage(name="Won", priority=9, type=WON, is_default=False, is_active=True, business_id=business_id),
            Stage(name="Lost", priority=10, type=LOST, is_default=False, is_active=True, business_id=business_id),
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
