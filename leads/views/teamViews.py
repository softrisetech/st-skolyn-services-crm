from django.db.models import Q
from rest_framework import status
from django.db import transaction
from ..serializers import TeamSerializer
from ..models import Team, Lead, TeamMember
from rest_framework.decorators import api_view
from core.utils.pagination_utils import CustomPagination
from core.utils.helpers import has_active_child_references
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from ..utils.filters import filter_by_active, filter_by_sort_order, filter_by_branches
from core.utils.response_utils import success_response, error_response


def __queryset(business_id):
    return Team.objects.filter(business_id=business_id)


def __apply_filters(queryset, filters):
    search_query = filters.get('search')
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) | 
            Q(slug__icontains=search_query) |
            Q(description__icontains=search_query) 
        )

    queryset = filter_by_branches(queryset, filters)
    queryset = filter_by_active(queryset, filters)
    queryset = filter_by_sort_order(queryset, filters)
    return queryset


@api_view(['POST'])
@access_control_middleware
def get_lead_teams(request):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')
    queryset = __queryset(business_id)
    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = TeamSerializer(paginated_queryset, many=True).data
    for data in serialized_data:
        data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
        data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)
    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)


@api_view(['POST'])
@access_control_middleware
def get_lead_team(request, pk=None):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')
    team = __queryset(business_id).filter(id=pk).first()
    if not team:
        return error_response('team_not_found', status.HTTP_404_NOT_FOUND)

    serialized_data = TeamSerializer(team).data
    serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], timezone)
    serialized_data["updated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["updated_at"], timezone)
    return success_response('record_fetched', status.HTTP_200_OK, serialized_data)


@api_view(['POST'])
@access_control_middleware
def store_lead_team(request):
    data = request.data.copy()
    data['business_id'] = data.get('auth_business_id')

    serializer = TeamSerializer(data=data)
    if not serializer.is_valid():
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    try:
        with transaction.atomic():

            team = serializer.save()

            bulk_create_team_members(
                data['business_id'],
                team.id,
                data.get('member_ids', [])
            )

        return success_response('record_stored', status.HTTP_201_CREATED, serializer.data)

    except Exception as e:
        return error_response('record_store_failed', status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@access_control_middleware
def update_lead_team(request, pk=None):
    data = request.data.copy()
    business_id = data.get('auth_business_id')

    team = __queryset(business_id).filter(id=pk).first()
    if not team:
        return error_response('team_not_found', status.HTTP_404_NOT_FOUND)

    data['business_id'] = business_id
    serializer = TeamSerializer(instance=team, data=data, partial=False)

    if not serializer.is_valid():
        return error_response('record_updation_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    try:
        with transaction.atomic():

            updated_team = serializer.save()

            remove_existing_team_members(business_id, updated_team.id)

            bulk_create_team_members(
                business_id,
                updated_team.id,
                data.get('member_ids', [])
            )

        return success_response('record_updated', status.HTTP_200_OK, serializer.data)

    except Exception as e:
        return error_response('record_updation_failed', status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@access_control_middleware
def delete_lead_team(request, pk=None):
    business_id = request.data.get('auth_business_id')
    team = __queryset(business_id).filter(id=pk).first()
    if not team:
        return error_response('team_not_found', status.HTTP_404_NOT_FOUND)

    child_references = [
        {'model': Lead, 'foreign_key': 'team_id'},
        {'model': TeamMember, 'foreign_key': 'team_id'}
    ]
    has_refs = has_active_child_references(child_references, pk, business_id)
    if has_refs:
        return error_response("related_team_record_found_on_deletion", status.HTTP_400_BAD_REQUEST)

    team.delete()
    return success_response('record_deleted', status.HTTP_200_OK)


def bulk_create_team_members(business_id, team_id, member_ids):

    # Remove duplicates & empty values
    unique_member_ids = list({mid for mid in member_ids if mid})

    team_members = [
        TeamMember(
            business_id=business_id,
            team_id=team_id,
            user_id=member_id
        )
        for member_id in unique_member_ids
    ]

    if team_members:
        TeamMember.objects.bulk_create(team_members)


def remove_existing_team_members(business_id, team_id):
    TeamMember.objects.filter(team_id=team_id, business_id=business_id).delete()