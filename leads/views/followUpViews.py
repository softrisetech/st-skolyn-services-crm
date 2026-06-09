from rest_framework import status
from ..serializers import FollowUpSerializer
from rest_framework.decorators import api_view
from ..models import FollowUp, Lead, FollowUpType
from core.utils.pagination_utils import CustomPagination
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from core.utils.response_utils import success_response, error_response
from core.utils.notification_utils import notification, notification_obj
from ..utils.lead_utils import (
    handle_lead_email_notifications,
    handle_lead_web_notifications
)
from ..utils.filters import (
    filter_by_created_bys, 
    filter_by_start_and_end_date, 
    filter_by_follow_up_types, 
    filter_by_done,
    lead_follow_up_search_filter,
    filter_by_sort_order
)

def __queryset(business_id, lead_id, use_report_db=False):
    db_alias = 'report_connection' if use_report_db else 'default'
    return FollowUp.objects.using(db_alias).filter(business_id=business_id, lead_id=lead_id)

def __apply_filters(queryset, filters):
    queryset = lead_follow_up_search_filter(queryset, filters)
    queryset = filter_by_created_bys(queryset, filters)
    queryset = filter_by_start_and_end_date(queryset, filters)
    queryset = filter_by_follow_up_types(queryset, filters)
    queryset = filter_by_done(queryset, filters)
    queryset = filter_by_sort_order(queryset, filters)
    return queryset

@api_view(['POST'])
@access_control_middleware
def get_lead_follow_ups(request, lead_id):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')

    lead = Lead.objects.filter(id=lead_id, business_id=business_id).first()
    if not lead:
        return error_response('lead_not_found', status.HTTP_404_NOT_FOUND)
    
    queryset = __queryset(business_id, lead_id)
    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = FollowUpSerializer(paginated_queryset, many=True).data
    for data in serialized_data:
        data["date_time"] = DateTimeConverter.from_utc_datetime(data["date_time"], timezone)
        data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
        data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)

    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)

@api_view(['POST'])
@access_control_middleware
def get_lead_follow_up(request, lead_id, pk):
    data = request.data
    timezone = data.get("auth_timezone")
    business_id = data.get('auth_business_id')
    queryset = __queryset(business_id, lead_id)
    follow_up = queryset.get(id=pk)
    if not follow_up:
        return error_response('follow_up_not_found', status.HTTP_404_NOT_FOUND)
    
    serialized_data = FollowUpSerializer(follow_up).data
    serialized_data["date_time"] = DateTimeConverter.from_utc_datetime(serialized_data["date_time"], timezone)
    serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], timezone)
    serialized_data["updated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["updated_at"], timezone)
    return success_response('record_fetched', status.HTTP_200_OK, serialized_data)
        
    

@api_view(['POST'])
@access_control_middleware
def store_lead_follow_up(request, lead_id):
    data = request.data.copy()
    data['business_id'] = request.data.get('auth_business_id')
    data['created_by'] = request.data.get('auth_id')
    data['follow_up_type'] = request.data.get('follow_up_type')
    user_timezone = data.get("auth_timezone")
    date_time = data["date_time"]
    web_notifications, email_notifications, other = [], [], {}

    follow_up_type = FollowUpType.objects.filter(id=data['follow_up_type'], business_id=data['business_id']).first()
    if not follow_up_type:
        return error_response('follow_up_type_not_found', status.HTTP_404_NOT_FOUND)

    lead = Lead.objects.filter(id=lead_id, business_id=data['business_id']).first()
    if not lead:
        return error_response('lead_not_found', status.HTTP_404_NOT_FOUND)

    data['lead'] = lead.id
    data["date_time"] = DateTimeConverter.to_utc_datetime(date_time, user_timezone)
    serializer = FollowUpSerializer(data=data)
    if not serializer.is_valid():
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    follow_up = serializer.save()

    email_notifications = handle_lead_email_notifications(data, user_timezone, ["assigned_to"], email_notifications, "follow_up_created", lead, None, None, follow_up_type.name, date_time, follow_up.description)
    web_notifications = handle_lead_web_notifications(data, user_timezone, ["assigned_to"], web_notifications, "follow_up_created", lead)
    other['notification'] = notification(email_notifications, web_notifications)
    return success_response('record_stored', status.HTTP_201_CREATED, serializer.data, other)

@api_view(['POST'])
@access_control_middleware
def update_lead_follow_up(request, lead_id, pk):
    data = request.data.copy()
    business_id = request.data.get('auth_business_id')
    user_timezone = data.get("auth_timezone")
    data['business_id'] = business_id
    data['follow_up_type'] = request.data.get('follow_up_type')

    follow_up = FollowUp.objects.filter(id=pk, business_id=business_id, lead_id=lead_id).first()
    if not follow_up:
        return error_response('follow_up_not_found', status.HTTP_404_NOT_FOUND)
    
    follow_up_type = FollowUpType.objects.filter(id=data['follow_up_type'], business_id=data['business_id']).first()
    if not follow_up_type:
        return error_response('follow_up_type_not_found', status.HTTP_404_NOT_FOUND)

    data['lead'] = follow_up.lead_id
    data['created_by'] = follow_up.created_by
    data["date_time"] = DateTimeConverter.to_utc_datetime(data["date_time"], user_timezone)
    serializer = FollowUpSerializer(instance=follow_up, data=data, partial=False)
    if not serializer.is_valid():
        return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

    serializer.save()
    return success_response('record_updated', status.HTTP_200_OK, serializer.data)


@api_view(['POST'])
@access_control_middleware
def delete_lead_follow_up(request, lead_id, pk):
    business_id = request.data.get('auth_business_id')
    follow_up = FollowUp.objects.filter(id=pk, business_id=business_id, lead_id=lead_id).first()
    if not follow_up:
        return error_response('follow_up_not_found', status.HTTP_404_NOT_FOUND)
    
    follow_up.delete()
    return success_response('record_deleted', status.HTTP_200_OK)

# class FollowUpView(APIView):
#     pagination_class = CustomPagination

#     def get_queryset(self, business_id, lead_id):
#         """Retrieve the base queryset filtered by business_id."""
#         return FollowUp.objects.filter(business_id=business_id, lead_id=lead_id)

#     def apply_filters(self, queryset, filters):
#         queryset = filter_by_followup_bys(queryset, filters)
#         queryset = filter_by_start_and_end_date(queryset, filters)
#         queryset = filter_by_type(queryset, filters)
#         queryset = filter_by_duration(queryset, filters)
#         return queryset

#     @method_decorator(access_control_middleware)
#     def get(self, request, pk=None):
#         data = request.query_params
#         timezone = data.get("auth_timezone")
#         business_id = data.get('auth_business_id')
#         lead_id = data.get('lead_id')
#         queryset = self.get_queryset(business_id, lead_id)

#         if pk:
#             try:
#                 follow_up = FollowUp.objects.get(id=pk)
#                 serialized_data = FollowUpSerializer(follow_up).data
#                 serialized_data["date"] = DateTimeConverter.from_utc_date(serialized_data["date"], timezone)
#                 serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], timezone)
#                 serialized_data["updated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["updated_at"], timezone)
#                 return success_response('record_fetched', status.HTTP_200_OK, serialized_data)
#             except FollowUp.DoesNotExist:
#                 return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

#         # List view with pagination and filters
#         filters = data
#         queryset = self.apply_filters(queryset, filters)
#         paginator = self.pagination_class()
#         paginated_queryset = paginator.paginate_queryset(queryset, request)
#         serialized_data = FollowUpSerializer(paginated_queryset, many=True).data
#         for data in serialized_data:
#             data["date"] = DateTimeConverter.from_utc_date(data["date"], timezone)
#             data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
#             data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)

#         response_data = paginator.get_paginated_response(serialized_data)
#         return success_response('record_fetched', status.HTTP_200_OK, response_data)

#     @method_decorator(access_control_middleware)
#     def post(self, request):
#         data = request.data.copy()
#         data['business_id'] = request.data.get('auth_business_id')
#         data['follow_up_by'] = request.data.get('auth_id')
#         data['type'] = request.data.get('type')
#         other = {}

#         try:
#             follow_up_type = FollowUpType.objects.get(id=data['type_id'], business_id=data['business_id'])
#         except FollowUpType.DoesNotExist:
#             return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

#         try:
#             lead = Lead.objects.get(id=data['lead_id'], business_id=data['business_id'])
#         except Lead.DoesNotExist:
#             return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

#         serializer = FollowUpSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             subject = "follow_ups_created"
#             path = f"crm/lead/{lead.id}/edit"

#             if data["type"] in [2, "2"]:
#                 subject = "opportunity_follow_ups_created"
#                 path = f"crm/opportunities/{lead.id}/edit"

#             follow_ups_created_notification = notification_obj(
#                 subject,
#                 [],
#                 {
#                     'business_id': lead.business_id,
#                     'branch_id': lead.branch_id,
#                     'name': lead.name,
#                     'follow_up_type': follow_up_type.name,
#                     'follow_up_date': request.data.get('date'),
#                     'remarks': request.data.get('description'),
#                     'path': path
#                 }
#             )
#             other["notifications"] = notification(follow_ups_created_notification, follow_ups_created_notification)
#             return success_response('record_stored', status.HTTP_201_CREATED, serializer.data, other)
#         return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

#     @method_decorator(access_control_middleware)
#     def put(self, request, pk=None):
#         business_id = request.data.get('auth_business_id')
#         data = request.data.copy()
#         data['business_id'] = business_id
#         data['follow_up_by'] = request.data.get('auth_id')
#         data['type'] = request.data.get('type')

#         try:
#             FollowUpType.objects.get(id=data['type_id'], business_id=data['business_id'])
#         except FollowUpType.DoesNotExist:
#             return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

#         try:
#             follow_up = FollowUp.objects.get(id=pk, business_id=business_id)
#         except FollowUp.DoesNotExist:
#             return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

#         data['lead_id'] = follow_up.lead_id
#         serializer = FollowUpSerializer(instance=follow_up, data=data, partial=False)
#         if serializer.is_valid():
#             serializer.save()
#             return success_response('record_updated', status.HTTP_200_OK, serializer.data)
#         return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

#     @method_decorator(access_control_middleware)
#     def delete(self, request, pk=None):
#         business_id = request.data.get('auth_business_id')
#         try:
#             follow_up = FollowUp.objects.get(id=pk, business_id=business_id)
#             follow_up.delete()
#             return success_response('record_deleted', status.HTTP_200_OK)
#         except FollowUp.DoesNotExist:
#             return error_response('record_not_found', status.HTTP_404_NOT_FOUND)
