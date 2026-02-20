import asyncio
import json, math
from django.db import transaction
from rest_framework import status
from django.utils import timezone
from django.db import IntegrityError
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from core.utils.helpers import check_if_user_is_staff
from leads.utils.lead_utils import handle_email_trigger, get_default_lead_stage, get_default_lead_stage_by_priority
from core.utils.pagination_utils import CustomPagination
from django.db.models import Q, Case, When, IntegerField
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from core.utils.response_utils import success_response, error_response
from core.utils.notification_utils import notification, notification_obj
from core.constants.model_constants import STAGE, MEDIUM, SOURCE, TAG, BRANCH
from ..serializers import LeadListSerializer, LeadStoreSerializer, StageLeadSerializer, LeadImportSerializer, ContactSerializer
from access_control.utils.permission_helpers import view_branch_wise, view_modify_all
from ..models import Lead, Stage, Source, Medium, Attachment, Tracking, Tag, StageReason, Team, Campaign
from core.utils.model_helpers import lead_default_stage, tracking_object, verify_lead_missing_fields
from access_control.utils.permission_constants import LEAD_VIEW_ALL, LEAD_BRANCH_WISE, LEAD_MODIFY_ALL
from leads.utils.filters import filter_by_sort_order, filter_by_campaigns, filter_by_teams, filter_by_priority, filter_by_countries, filter_by_states, filter_by_cities, lead_search_filter, filter_by_date_range, filter_by_branches, filter_by_created_by, filter_by_assigned_to, filter_by_mediums, filter_by_generated, filter_by_sessions, filter_by_sources, filter_by_stages, filter_by_tags


def __queryset(business_id):
    return Lead.objects.filter(business_id=business_id)


def __apply_filters(queryset, filters):
    queryset = lead_search_filter(queryset, filters)
    queryset = filter_by_branches(queryset, filters)
    queryset = filter_by_sessions(queryset, filters)
    queryset = filter_by_created_by(queryset, filters)
    queryset = filter_by_assigned_to(queryset, filters)
    queryset = filter_by_countries(queryset, filters)
    queryset = filter_by_states(queryset, filters)
    queryset = filter_by_cities(queryset, filters)
    queryset = filter_by_priority(queryset, filters)
    queryset = filter_by_mediums(queryset, filters)
    queryset = filter_by_sources(queryset, filters)
    queryset = filter_by_stages(queryset, filters)
    queryset = filter_by_tags(queryset, filters)
    queryset = filter_by_teams(queryset, filters)
    queryset = filter_by_campaigns(queryset, filters)
    queryset = filter_by_date_range(queryset, filters)
    queryset = filter_by_sort_order(queryset, filters)

    return queryset


@api_view(['POST'])
@access_control_middleware
def get_leads(request):
    data = request.data
    business_id = data.get('auth_business_id')
    queryset = __queryset(business_id)
    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = LeadListSerializer(paginated_queryset, many=True).data
    for data in serialized_data:
        if data["generated_at"]:
            data["generated_at"] = DateTimeConverter.from_utc_datetime(data["generated_at"], timezone)

        if data["imported_at"]:
            data["imported_at"] = DateTimeConverter.from_utc_datetime(data["imported_at"], timezone)

        data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
        data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)

    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)


@api_view(['POST'])
@access_control_middleware
def store_lead(request):
    data = request.data.copy()
    auth_id = data.get('auth_id')
    business_id = data.get('auth_business_id')

    data['business_id'] = business_id
    data['created_by'] = auth_id

    lookup_map = {
        'medium': Medium,
        'source': Source,
        'tag': Tag,
        'team': Team,
        'campaign': Campaign
    }

    # ✅ Validate lookups BEFORE transaction
    for field, model in lookup_map.items():
        obj_id = data.get(field)
        if obj_id:
            exists = model.objects.filter(id=obj_id, business_id=business_id).exists()
            if not exists:
                return error_response(f'{field}_not_found', status.HTTP_404_NOT_FOUND)

    # ✅ Validate default stage
    default_stage = get_default_lead_stage(business_id) or get_default_lead_stage_by_priority(business_id)
    if not default_stage:
        return error_response('default_stage_missing', status.HTTP_422_UNPROCESSABLE_ENTITY)

    data["stage"] = default_stage.id

    contact_serializer = ContactSerializer(data=data)
    if not contact_serializer.is_valid():
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, contact_serializer.errors)

    with transaction.atomic():

        # ✅ Save Contact first
        contact = contact_serializer.save()

        # ✅ Inject contact id for lead
        data['contact'] = contact.id
        data['code'] = "abcd"

        # ✅ Now validate Lead
        lead_serializer = LeadStoreSerializer(data=data)
        if not lead_serializer.is_valid():
            return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, lead_serializer.errors)


        lead = lead_serializer.save()

        attachments = request.data.get('attachments')
        store_lead_attachments(business_id, lead.id, attachments)

    return success_response('record_stored', status.HTTP_201_CREATED, lead_serializer.data)


                    

                    


# # Helper function to retrieve the queryset filtered by business_id
# def get_queryset(request, business_id):
#     filters = {"business_id": business_id}
#     data = request.query_params or request.data
#     is_staff = check_if_user_is_staff(data)

#     if is_staff == "true":
#         user_id = data.get('auth_id')
#         role_id = data.get('auth_role_id')
#         have_view_all_permission = view_modify_all(user_id, role_id, LEAD_VIEW_ALL)
#         have_branch_wise_permission = view_branch_wise(user_id, role_id, LEAD_BRANCH_WISE)

#         queryset = Lead.objects.filter(**filters)

#         if not have_view_all_permission:
#             # Add OR condition: created_by=user_id OR assigned_to=user_id
#             queryset = queryset.filter(Q(created_by=user_id) | Q(assigned_to=user_id))

#         if have_branch_wise_permission:
#             branch_id = data.get("auth_branch_id")
#             queryset = queryset.filter(branch_id=branch_id)

#         return queryset

#     return Lead.objects.filter(**filters)

# # Helper function to apply search and filter conditions to the queryset
# def apply_filters(queryset, filters):
#     queryset = search_filter(queryset, filters)
#     queryset = filter_by_date_range(queryset, filters)
#     queryset = filter_by_branches(queryset, filters)
#     queryset = filter_by_created_by(queryset, filters)
#     queryset = filter_by_assigned_to(queryset, filters)
#     queryset = filter_by_mediums(queryset, filters)
#     queryset = filter_by_sources(queryset, filters)
#     queryset = filter_by_stages(queryset, filters)
#     queryset = filter_by_sessions(queryset, filters)
#     queryset = filter_by_tags(queryset, filters)
#     queryset = filter_by_generated(queryset, filters)
#     return queryset

# # GET View
# @api_view(['GET'])
# @access_control_middleware
# def lead_list_stage_wise(request, pk=None):
#     business_id = request.query_params.get('auth_business_id')
#     if not business_id:
#         return error_response('auth_business_id_missing', status.HTTP_422_UNPROCESSABLE_ENTITY)

#     queryset = get_queryset(request, business_id)

#     #Get pagination params
#     page = int(request.query_params.get('page', 1))
#     page_size = int(request.query_params.get('page_size', 20))
#     skip = (page - 1) * page_size
#     take = skip + page_size

#     if pk:
#         stage_leads = queryset.filter(stage=pk)[skip:take]
#         serialized_data = StageLeadSerializer(stage_leads, many=True).data
#         data = {
#              "items": serialized_data,
#              "pagination": {
#                  "page": page,
#                  "page_size": page_size,
#                  "all_items_count": queryset.filter(stage=pk).count(),
#                  "total_pages": math.ceil(queryset.filter(stage=pk).count()/page_size),
#                  "remaining_items_count": max(queryset.filter(stage=pk).count() - (page_size * page), 0)
#              }
#         }
#         return success_response('record_fetched', status.HTTP_200_OK, data)

#     filters = request.query_params
#     queryset = apply_filters(queryset, filters)
#     stages = Stage.objects.filter(business_id=business_id, is_active=1).order_by(
#         Case(
#             When(status="open", then=0),
#             When(status="registration", then=1),
#             When(status="lost", then=2),
#             default=3,
#             output_field=IntegerField(),
#         ),
#         "priority"
#     )

#     grouped_leads = {"stages": []}
#     for stage in stages:
#         stage_leads = queryset.filter(stage=stage.id)[skip:take]  # Apply Skip-Take (Offset-Limit)
#         serialized_data = StageLeadSerializer(stage_leads, many=True).data
#         total_items = queryset.filter(stage=stage.id).count()

#         grouped_leads["stages"].append({  # Append each stage's data to the list
#             "id": stage.id,
#             "name": stage.name,
#             "type": stage.status,
#             "items": serialized_data,
#             "pagination": {
#                 "page": page,
#                 "page_size": page_size,
#                 "all_items_count": total_items,
#                 "total_pages": math.ceil(total_items / page_size),
#                 "remaining_items_count": max(total_items - skip - page_size, 0)
#             }
#         })

#     return success_response('record_fetched', status.HTTP_200_OK, grouped_leads)


# # GET View
# @api_view(['GET'])
# @access_control_middleware
# def lead_list(request, pk=None):
#     data = request.query_params
#     timezone = data.get("auth_timezone")
#     """Retrieve a list of leads or a specific lead."""
#     business_id = data.get('auth_business_id')
#     if not business_id:
#         return error_response('auth_business_id_missing', status.HTTP_422_UNPROCESSABLE_ENTITY)

#     queryset = get_queryset(request, business_id)

#     # Retrieve a specific lead if pk is provided
#     if pk:
#         lead = queryset.filter(id=pk).first()
#         if lead:
#             serialized_data = LeadSerializer(lead).data
#             if serialized_data["generated_at"]:
#                 serialized_data["generated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["generated_at"], timezone)

#             if serialized_data["imported_at"]:
#                 serialized_data["imported_at"] = DateTimeConverter.from_utc_datetime(serialized_data["imported_at"], timezone)

#             serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], timezone)
#             serialized_data["updated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["updated_at"], timezone)
#             return success_response('record_fetched', status.HTTP_200_OK, serialized_data)
#         return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

#     # List view with pagination and filters
#     filters = data
#     queryset = apply_filters(queryset, filters)
#     paginator = CustomPagination()
#     paginated_queryset = paginator.paginate_queryset(queryset, request)
#     serialized_data = LeadSerializer(paginated_queryset, many=True).data
#     for data in serialized_data:
#         if data["generated_at"]:
#             data["generated_at"] = DateTimeConverter.from_utc_datetime(data["generated_at"], timezone)

#         if data["imported_at"]:
#             data["imported_at"] = DateTimeConverter.from_utc_datetime(data["imported_at"], timezone)

#         data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], timezone)
#         data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], timezone)

#     response_data = paginator.get_paginated_response(serialized_data)
#     return success_response('record_fetched', status.HTTP_200_OK, response_data)

# # POST View
# @api_view(['POST'])
# @access_control_middleware
# def lead_create(request):
#     data = request.data.copy()
#     auth_id = data.get('auth_id')
#     business_id = data.get('auth_business_id')
#     data['business_id'] = business_id
#     data['created_by'] = auth_id

#     #check if medium exists
#     medium = Medium.objects.filter(id=data.get('medium'), business_id=business_id).first()
#     if not medium:
#         return error_response('record_not_found', status.HTTP_404_NOT_FOUND)
#     #check if source exists
#     source = Source.objects.filter(id=data.get('source'), business_id=business_id).first()
#     if not source:
#         return error_response('record_not_found', status.HTTP_404_NOT_FOUND)
#     #check if tag exists
#     if data.get('tag'):
#         tag = Tag.objects.filter(id=data.get('tag'), business_id=business_id).first()
#         if not tag:
#             return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

#     try:
#         default_stage = Stage.objects.filter(
#             business_id=business_id,
#             is_default=True,
#             is_active=True
#         ).first()

#         # If no default stage found, get first stage sorted by priority
#         if not default_stage:
#             default_stage = Stage.objects.filter(
#                 business_id=business_id,
#                 status="open",
#                 is_active=True
#             ).order_by('priority').first()

#         if default_stage:
#             defaultStageId = default_stage.id
#         else:
#             return error_response('default_stage_missing', status.HTTP_422_UNPROCESSABLE_ENTITY)

#     except Exception as e:
#         return error_response(f"An error occurred: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

#     data['stage'] = defaultStageId
#     serializer = LeadSerializer(data=data)
#     if serializer.is_valid():
#         with transaction.atomic():  # Ensures atomicity
#             lead = serializer.save()

#             lead_attachments_object = []

#             lead_attachments = request.data.get('documents', '')

#             # Convert to list if it's a non-empty string, otherwise keep it as an empty list
#             lead_attachments = lead_attachments.split(',') if lead_attachments else []
#             for attachment in lead_attachments:
#                 lead_attachments_object.append(Attachment(business_id=business_id,lead_id=lead.id, path=attachment))

#             # Bulk create lead attachment records
#             Attachment.objects.bulk_create(lead_attachments_object)
#             lead_tracking_objects = []

#             if defaultStageId:
#                 lead_tracking_objects.append(Tracking(
#                     business_id=lead.business_id,
#                     lead_id=lead.id,
#                     model_id=defaultStageId,
#                     model_type=STAGE,
#                     user_id=auth_id
#                 ))

#             if lead.source_id:
#                 lead_tracking_objects.append(Tracking(
#                      business_id=lead.business_id,
#                      lead_id=lead.id,
#                      model_id=lead.source_id,
#                      model_type=SOURCE,
#                      user_id=auth_id
#                 ))

#             if lead.medium_id:
#                 lead_tracking_objects.append(Tracking(
#                      business_id=lead.business_id,
#                      lead_id=lead.id,
#                      model_id=lead.medium_id,
#                      model_type=MEDIUM,
#                      user_id=auth_id
#                 ))

#             if lead.tag_id:
#                 lead_tracking_objects.append(Tracking(
#                      business_id=lead.business_id,
#                      lead_id=lead.id,
#                      model_id=lead.tag_id,
#                      model_type=TAG,
#                      user_id=auth_id
#                 ))

#             if lead.branch_id:
#                 lead_tracking_objects.append(Tracking(
#                      business_id=lead.business_id,
#                      lead_id=lead.id,
#                      model_id=lead.branch_id,
#                      model_type=BRANCH,
#                      user_id=auth_id
#                 ))
#             other = {}
#             notifications = []
#             lead_create_notification = notification_obj(
#                 "lead_created",
#                 [lead.created_by],
#                 {
#                     'business_id': business_id,
#                     'branch_id': lead.branch_id,
#                     'lead_name': lead.name,
#                     'path': f"crm/lead/{lead.id}/edit"
#                 }
#             )

#             notifications.append(lead_create_notification)

#             # Only add email/web if lead is assigned
#             if lead.assigned_to:
#                 lead_assigned_notification = notification_obj(
#                     "lead_assigned",
#                     [lead.assigned_to],
#                     {
#                         'business_id': business_id,
#                         'branch_id': lead.branch_id,
#                         'lead_name': lead.name,
#                         'path': f"crm/lead/{lead.id}/edit"
#                     }
#                 )
#                 notifications.append(lead_assigned_notification)

#             other["notification"] = notification(notifications, notifications)
#             # Bulk create lead tracking records
#             Tracking.objects.bulk_create(lead_tracking_objects)

#         return success_response('record_stored', status.HTTP_201_CREATED, serializer.data, other)

#     return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

# # PUT View
# @api_view(['PUT'])
# @access_control_middleware
# def lead_update(request, pk):
#     data = request.data.copy()
#     business_id = data.get('auth_business_id')
#     auth_id = data.get('auth_id')
#     data['business_id'] = business_id
#     role_id = data.get('auth_role_id')
#     is_staff = check_if_user_is_staff(data)
#     try:
#         lead = Lead.objects.get(id=pk, business_id=business_id)
#         if is_staff == "true":
#             have_modify_all_permission = view_modify_all(auth_id, role_id, LEAD_MODIFY_ALL)
#             if str(lead.created_by) != str(auth_id) and not have_modify_all_permission:
#                 return error_response('permission_denied', status.HTTP_403_FORBIDDEN)
#     except Lead.DoesNotExist:
#         return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

#     #check if medium exists
#     medium = Medium.objects.filter(id=data.get('medium'), business_id=business_id).first()
#     if not medium:
#         return error_response('record_not_found', status.HTTP_404_NOT_FOUND)
#     #check if source exists
#     source = Source.objects.filter(id=data.get('source'), business_id=business_id).first()
#     if not source:
#         return error_response('record_not_found', status.HTTP_404_NOT_FOUND)
#     #check if tag exists
#     if data.get('tag'):
#         tag = Tag.objects.filter(id=data.get('tag'), business_id=business_id).first()
#         if not tag:
#             return error_response('record_not_found', status.HTTP_404_NOT_FOUND)

#     # Store old lead values before updating
#     old_lead_data = {
#         "stage_id": lead.stage_id,
#         "source_id": lead.source_id,
#         "medium_id": lead.medium_id,
#         "tag_id": lead.tag_id,
#         "branch_id": lead.branch_id,
#         "assigned_to": lead.assigned_to,
#     }

#     # Remove stage_id from the request data to prevent it from being updated
#     data.pop('stage_id', None)
#     serializer = LeadSerializer(instance=lead, data=data, partial=False)

#     if serializer.is_valid():
#         with transaction.atomic():  # Ensure atomicity
#             updatedLead = serializer.save()

#             lead_attachments_object = []
#             lead_attachments = request.data.get('documents', '')
#             lead_attachments = lead_attachments.split(',') if lead_attachments else []
#             if lead_attachments:
#                 for attachment in lead_attachments:
#                     lead_attachments_object.append(
#                         Attachment(business_id=business_id, lead_id=updatedLead.id, path=attachment)
#                     )

#                 if lead_attachments_object:
#                     Attachment.objects.bulk_create(lead_attachments_object)

#             lead_tracking_objects = []
#             # Store lead tracking data if stage_id changed
#             if updatedLead.stage_id != old_lead_data["stage_id"]:
#                 lead_tracking_objects.append(
#                     Tracking(
#                         business_id=updatedLead.business_id,
#                         lead_id=updatedLead.id,
#                         model_id=updatedLead.stage_id,
#                         model_type=STAGE,
#                         user_id=auth_id
#                     )
#                 )

#             # Store lead tracking data if source_id changed
#             if updatedLead.source_id != old_lead_data["source_id"]:
#                 lead_tracking_objects.append(
#                     Tracking(
#                         business_id=updatedLead.business_id,
#                         lead_id=updatedLead.id,
#                         model_id=updatedLead.source_id,
#                         model_type=SOURCE,
#                         user_id=auth_id
#                     )
#                 )

#             # Store lead tracking data if medium_id changed
#             if updatedLead.medium_id != old_lead_data["medium_id"]:
#                 lead_tracking_objects.append(
#                     Tracking(
#                         business_id=updatedLead.business_id,
#                         lead_id=updatedLead.id,
#                         model_id=updatedLead.medium_id,
#                         model_type=MEDIUM,
#                         user_id=auth_id
#                     )
#                 )

#             # Store lead tracking data if tag_id changed
#             if request.data.get('tag_id') and updatedLead.tag_id != old_lead_data["tag_id"]:
#                 lead_tracking_objects.append(
#                     Tracking(
#                         business_id=updatedLead.business_id,
#                         lead_id=updatedLead.id,
#                         model_id=updatedLead.tag_id,
#                         model_type=TAG,
#                         user_id=auth_id
#                     )
#                 )

#             # Store lead tracking data if branch_id changed
#             if updatedLead.branch_id != old_lead_data["branch_id"]:
#                 lead_tracking_objects.append(
#                     Tracking(
#                         business_id=updatedLead.business_id,
#                         lead_id=updatedLead.id,
#                         model_id=updatedLead.branch_id,
#                         model_type=BRANCH,
#                         user_id=auth_id
#                     )
#                 )

#             other = {}
#             if updatedLead.assigned_to and str(updatedLead.assigned_to) != str(old_lead_data["assigned_to"]):
#                 email_web_obj = notification_obj(
#                         "lead_assigned",
#                         [updatedLead.assigned_to],
#                         {
#                             'business_id': updatedLead.business_id,
#                             'branch_id': updatedLead.branch_id,
#                             'lead_name': updatedLead.name,
#                             'path': f"crm/lead/{updatedLead.id}/edit"
#                         }
#                     )
#                 other['notification'] = notification(email_web_obj, email_web_obj)
        
#             # Bulk create all Tracking records at once
#             if lead_tracking_objects:
#                 Tracking.objects.bulk_create(lead_tracking_objects)

#         return success_response('record_updated', status.HTTP_200_OK, serializer.data, other)

#     return error_response('record_update_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

# # DELETE View
# @api_view(['DELETE'])
# @access_control_middleware
# def lead_delete(request, pk):
#     data = request.data
#     business_id = data.get('auth_business_id')
#     role_id = data.get('auth_role_id')
#     is_staff = check_if_user_is_staff(data)
#     auth_id = data.get('auth_id')

#     try:
#         lead = Lead.objects.get(id=pk, business_id=business_id)
#         if is_staff == "true":
#             have_modify_all_permission = view_modify_all(auth_id, role_id, LEAD_MODIFY_ALL)
#             if have_modify_all_permission:
#                 lead.delete()
#                 return success_response('record_deleted', status.HTTP_200_OK)
#             else:
#                 if str(lead.created_by) == str(auth_id) or str(lead.assigned_to) == str(auth_id):
#                     lead.delete()
#                     return success_response('record_deleted', status.HTTP_200_OK)
#                 else:
#                     return error_response('permission_denied', status.HTTP_403_FORBIDDEN)

#         lead.delete()
#         return success_response('record_deleted', status.HTTP_200_OK)

#     except Lead.DoesNotExist:
#         return error_response('record_not_found', status.HTTP_404_NOT_FOUND)


# # Import Leads Function
# @api_view(['POST'])
# @access_control_middleware
# def import_leads(request):
#     data = request.data
#     business_id = data.get('auth_business_id')
#     user_timezone = data.get("auth_timezone")
#     branch_id = data.get('branch_id')
#     user_id = data.get('auth_id')
#     leads_data = data.get('leads', [])
#     file_errors = []

#     # --- Bulk fetch reference data for faster lookup ---
#     mediums = dict(
#         Medium.objects.filter(business_id=business_id).values_list("name", "id")
#     )
#     sources = dict(
#         Source.objects.filter(business_id=business_id).values_list("name", "id")
#     )
#     tags = dict(
#         Tag.objects.filter(business_id=business_id).values_list("name", "id")
#     )
#     stages = {s.name: s for s in Stage.objects.filter(business_id=business_id)}

#     # --- Validate leads ---
#     for idx, lead_data in enumerate(leads_data, start=2):  # start=2 if row 1 is header
#         row_errors = {}
#         if lead_data.get('medium') and lead_data['medium'] not in mediums:
#             row_errors['medium'] = f"Medium '{lead_data['medium']}' does not exist."
#         if lead_data.get('source') and lead_data['source'] not in sources:
#             row_errors['source'] = f"Source '{lead_data['source']}' does not exist."
#         if lead_data.get('tag') and lead_data['tag'] not in tags:
#             row_errors['tag'] = f"Tag '{lead_data['tag']}' does not exist."
#         if lead_data.get('stage') and lead_data['stage'] not in stages:
#             row_errors['stage'] = f"Stage '{lead_data['stage']}' does not exist."

#         if row_errors:
#             file_errors.append({"row": idx, "errors": row_errors})

#     if file_errors:
#         return error_response(
#             'import_data_missing',
#             status.HTTP_422_UNPROCESSABLE_ENTITY,
#             {"file_errors": file_errors}
#         )

#     # --- Create leads ---
#     leads_to_create = []
#     tracking_to_create = []

#     try:
#         for lead_data in leads_data:
#             medium_id = mediums.get(lead_data.get('medium'))
#             source_id = sources.get(lead_data.get('source'))
#             tag_id = tags.get(lead_data.get('tag'))
#             stage_obj = stages.get(lead_data.get('stage'))
#             is_opportunity = False

#             if stage_obj:
#                 stage_id = stage_obj.id
#                 if stage_obj.status == "convert":
#                     is_opportunity = True
#             else:
#                 stage_id = lead_default_stage(business_id)

#             created_at = DateTimeConverter.to_utc_datetime(
#                 lead_data.get("created_at") or timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 user_timezone
#             )

#             prepared_lead = {
#                 "business_id": business_id,
#                 "branch_id": branch_id,
#                 "medium": medium_id,
#                 "source": source_id,
#                 "stage": stage_id,
#                 "tag": tag_id,
#                 "is_opportunity": is_opportunity,
#                 "p_name": lead_data.get("p_name"),
#                 "p_contact_number": lead_data.get("p_contact_number"),
#                 "p_email": lead_data.get("p_email"),
#                 "created_at": created_at,
#                 "updated_at": created_at,
#                 "date_of_birth": lead_data.get("date_of_birth"),
#                 "name": lead_data.get("name"),
#                 "contact_number": lead_data.get("contact_number"),
#                 "email": lead_data.get("email"),
#                 "previous_education": lead_data.get("previous_education"),
#                 "created_by": user_id,
#                 "priority": 1,
#                 "is_imported": True,
#                 "imported_at": DateTimeConverter.to_utc_datetime(
#                     timezone.now().strftime("%Y-%m-%d %H:%M:%S"), user_timezone
#                 ),
#             }

#             serializer = LeadImportSerializer(data=prepared_lead)
#             if serializer.is_valid():
#                 leads_to_create.append(Lead(**serializer.validated_data))
#             else:
#                 return error_response('validation_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)

#         # Bulk create leads
#         generated_leads = Lead.objects.bulk_create(leads_to_create)

#         # Collect Tracking objects
#         for lead, lead_data in zip(generated_leads, leads_data):
#             medium_id = mediums.get(lead_data.get('medium'))
#             source_id = sources.get(lead_data.get('source'))
#             tag_id = tags.get(lead_data.get('tag'))
#             stage_obj = stages.get(lead_data.get('stage'))
#             stage_id = stage_obj.id if stage_obj else lead_default_stage(business_id)

#             if medium_id:
#                 tracking_to_create.append(tracking_object(business_id, lead.id, medium_id, MEDIUM, user_id))
#             if source_id:
#                 tracking_to_create.append(tracking_object(business_id, lead.id, source_id, SOURCE, user_id))
#             if stage_id:
#                 tracking_to_create.append(tracking_object(business_id, lead.id, stage_id, STAGE, user_id))
#             if tag_id:
#                 tracking_to_create.append(tracking_object(business_id, lead.id, tag_id, TAG, user_id))

#         if tracking_to_create:
#             Tracking.objects.bulk_create(tracking_to_create)

#         return success_response('leads_imported', status.HTTP_201_CREATED, {
#             'message': 'leads successfully imported'
#         })

#     except IntegrityError as e:
#         return error_response('integrity_error', status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))
#     except Exception as e:
#         return error_response('internal_error', status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

# @api_view(['POST'])
# @access_control_middleware
# def export_leads(request):
#     data = request.data.copy()
#     try:
#         data["report_type"] = constants()["report_type"]["crm"]["leads"]
#         entry = asyncio.run(export_entry(data))
#         data["export_entry_id"] = entry.id
#         result = export_obj(data["report_type"], data)
#         return success_response(
#             'record_fetched',
#             status.HTTP_200_OK,
#             result
#         )
#     except Exception as e:
#         return error_response(str(e),  status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['PATCH'])
# @access_control_middleware
# def lead_change_stage(request, pk=None):
#     data = request.data
#     business_id = data.get('auth_business_id')
#     stage_id = data.get('stage_id')
#     auth_id = data.get('auth_id')
#     notifications, other = [], {}

#     # Load lead and stage
#     lead = get_object_or_404(Lead, id=pk, business_id=business_id)
#     lead_stage = get_object_or_404(Stage, id=stage_id, business_id=business_id)

#     # Validate required fields
#     missing_fields = verify_lead_missing_fields(lead)
#     if missing_fields and lead_stage.status != "lost":
#         return error_response('missing_required_fields', status.HTTP_400_BAD_REQUEST)

#     old_stage_id = lead.stage_id
#     if old_stage_id == lead_stage.id:
#         return error_response('same_stage_change', status.HTTP_422_UNPROCESSABLE_ENTITY)

#     new_stage_id = lead_stage.id

#     # Stage-specific handling
#     try:
#         if lead_stage.status == "lost":
#             handle_lead_lost(request, lead, business_id, lead_stage, notifications)

#     except ValueError as e:
#         # Map errors properly (Sonar will like this too)
#         error_map = {
#             'opportunity_default_stage_missing': status.HTTP_422_UNPROCESSABLE_ENTITY,
#             'reason_type_missing': status.HTTP_422_UNPROCESSABLE_ENTITY,
#             'record_not_found': status.HTTP_404_NOT_FOUND
#         }
#         return error_response(str(e), error_map.get(str(e), status.HTTP_400_BAD_REQUEST))

#     # Store lead tracking if stage changed
#     if old_stage_id != new_stage_id:
#         Tracking.objects.create(
#             business_id=lead.business_id,
#             lead_id=lead.id,
#             model_id=new_stage_id,
#             model_type=STAGE,
#             user_id=auth_id
#         )

#     # Save changes
#     lead.stage_id = new_stage_id
#     lead.save()

#     handle_email_trigger(request, lead, notifications)
#     other['notification'] = notification(notifications, notifications)
#     return success_response('stage_changed', status.HTTP_200_OK, [], other)


# # DELETE View
# @api_view(['DELETE'])
# @access_control_middleware
# def lead_delete_attachment(request, pk):
#     data = request.data
#     business_id = data.get('auth_business_id')
#     lead_id = data.get('lead_id')
#     try:
#         lead_attachments = Attachment.objects.get(id=pk, business_id=business_id, lead_id=lead_id)
#         lead_attachments.delete()
#         return success_response('record_deleted', status.HTTP_200_OK)
#     except Attachment.DoesNotExist:
#         return error_response('record_not_found', status.HTTP_404_NOT_FOUND)


# def handle_lead_lost(request, lead, auth_business_id, lead_stage, notifications):
#     type_id = request.data.get('type_id')
#     if not type_id:
#         raise ValueError('reason_type_missing')

#     lead_lost_reason = LostReason.objects.filter(
#         business_id=auth_business_id, id=type_id
#     ).first()
#     if not lead_lost_reason:
#         raise ValueError('record_not_found')

#     StageReason.objects.create(
#         lead_id=lead.id,
#         stage_id=lead_stage.id,
#         reason=request.data.get('reason'),
#         reason_type_id=type_id,
#         business_id=lead.business_id
#     )

#     notifications.append(notification_obj(
#         "lead_lost",
#         [],
#         {
#             'business_id': lead.business_id,
#             'branch_id': lead.branch_id,
#             'lead_name': lead.name,
#             'reason_type': lead_lost_reason.name,
#             'reason': request.data.get('reason'),
#             'path': f"crm/lead/{lead.id}/edit"
#         }
#     ))

def store_lead_attachments(business_id, lead_id, attachments):
    lead_attachments_object = []

    for attachment in attachments:
        lead_attachments_object.append(Attachment(business_id=business_id, lead_id=lead_id, file=attachment))

    if lead_attachments_object:
        Attachment.objects.bulk_create(lead_attachments_object)
