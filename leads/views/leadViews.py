import copy
import asyncio
import json, math
from django.db import transaction
from rest_framework import status
from django.utils import timezone
from django.db import IntegrityError
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from core.utils.helpers import check_if_user_is_staff
from leads.utils.lead_utils import handle_email_trigger, get_default_lead_stage, get_default_lead_stage_by_priority, generate_unique_code
from core.utils.pagination_utils import CustomPagination
from django.db.models import Q, Case, When, IntegerField
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter
from core.utils.response_utils import success_response, error_response
from core.utils.notification_utils import notification, notification_obj
from core.constants.model_constants import STAGE, MEDIUM, SOURCE, TAG, BRANCH, SESSION, ASSIGNED_TO, TEAM, CAMPAIGN
from ..serializers import LeadListSerializer, LeadStoreSerializer, LeadGetSerializer, StageLeadSerializer, LeadImportSerializer, ContactSerializer
from access_control.utils.permission_helpers import view_branch_wise, view_modify_all
from ..models import Lead, Stage, Source, Medium, Attachment, Tracking, Tag, StageReason, Team, Campaign, StageReasonEntry
from core.utils.model_helpers import lead_default_stage, tracking_object, verify_lead_missing_fields
from access_control.utils.permission_constants import LEAD_VIEW_ALL, LEAD_BRANCH_WISE, LEAD_MODIFY_ALL
from leads.utils.filters import filter_by_sort_order, filter_by_campaigns, filter_by_teams, filter_by_priority, filter_by_countries, filter_by_states, filter_by_cities, lead_search_filter, filter_by_date_range, filter_by_branches, filter_by_created_by, filter_by_assigned_to, filter_by_mediums, filter_by_generated, filter_by_sessions, filter_by_sources, filter_by_stages, filter_by_tags
from core.utils.helpers import has_active_child_references
from report_export.utils.constants import constants
from report_export.utils.export_helpers import export_entry, export_obj

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
    userTimezone = data.get("auth_timezone")
    queryset = __queryset(business_id)
    queryset = __apply_filters(queryset, data)
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serialized_data = LeadListSerializer(paginated_queryset, many=True).data
    for data in serialized_data:
        if data["imported_at"]:
            data["imported_at"] = DateTimeConverter.from_utc_datetime(data["imported_at"], userTimezone)

        data["created_at"] = DateTimeConverter.from_utc_datetime(data["created_at"], userTimezone)
        data["updated_at"] = DateTimeConverter.from_utc_datetime(data["updated_at"], userTimezone)

    response_data = paginator.get_paginated_response(serialized_data)
    return success_response('record_fetched', status.HTTP_200_OK, response_data)

@api_view(['POST'])
@access_control_middleware
def export_leads(request):
    data = request.data.copy()
    try:
        data["report_type"] = constants()["report_type"]["crm"]["leads"]
        entry = asyncio.run(export_entry(data))
        data["export_entry_id"] = entry.id
        result = export_obj(data["report_type"], data)
        return success_response('record_fetched', status.HTTP_200_OK, result)
    except Exception as e:
        return error_response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@access_control_middleware
def store_lead(request):
    data = request.data.copy()
    auth_id = data.get('auth_id')
    business_id = data.get('auth_business_id')
    base_payload = {**data, "business_id": business_id, "created_by": auth_id}
    lookup_map = {'medium': Medium, 'source': Source, 'tag': Tag, 'team': Team, 'campaign': Campaign}

    # ✅ Bulk lookup validation (reduces DB hits)
    for field, model in lookup_map.items():
        obj_id = base_payload.get(field)
        if obj_id and not model.objects.filter(id=obj_id, business_id=business_id).only('id').exists():
            return error_response(f'{field}_not_found', status.HTTP_404_NOT_FOUND)

    # ✅ Single optimized stage fetch
    default_stage = (get_default_lead_stage(business_id) or get_default_lead_stage_by_priority(business_id))
    if not default_stage:
        return error_response('default_stage_missing', status.HTTP_422_UNPROCESSABLE_ENTITY)

    base_payload["stage"] = default_stage.id

    # ✅ Validate Contact BEFORE transaction
    contact_serializer = ContactSerializer(data=base_payload)
    if not contact_serializer.is_valid():
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, contact_serializer.errors)

    with transaction.atomic():
        contact = contact_serializer.save()
        leads_payload = prepare_leads_to_store({**base_payload, "contact": contact.id})
        lead_serializer = LeadStoreSerializer(data=leads_payload, many=True)
        if not lead_serializer.is_valid():
            return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, lead_serializer.errors)

        leads = lead_serializer.save()
        attachments = data.get('attachments')
        store_leads_attachments(business_id, leads, attachments)
        store_leads_tracking(leads, auth_id)

    return success_response('record_stored', status.HTTP_201_CREATED, lead_serializer.data)

@api_view(['POST'])
@access_control_middleware
def get_lead(request, pk):
    data = request.data
    business_id = data.get('auth_business_id')
    userTimezone = data.get("auth_timezone")
    queryset = __queryset(business_id)
    lead = queryset.filter(id=pk).first()
    serialized_data = LeadGetSerializer(lead).data

    if serialized_data["imported_at"]:
        serialized_data["imported_at"] = DateTimeConverter.from_utc_datetime(serialized_data["imported_at"], userTimezone)

    serialized_data["created_at"] = DateTimeConverter.from_utc_datetime(serialized_data["created_at"], userTimezone)
    serialized_data["updated_at"] = DateTimeConverter.from_utc_datetime(serialized_data["updated_at"], userTimezone)

    return success_response('record_fetched', status.HTTP_200_OK, serialized_data)


@api_view(['POST'])
@access_control_middleware
def update_lead(request, pk):
    data = request.data.copy()
    business_id = data.get('auth_business_id')
    auth_id = data.get('auth_id')
    role_id = data.get('auth_role_id')
    is_staff = check_if_user_is_staff(data)

    quertset = __queryset(business_id)
    lead = quertset.filter(id=pk).first()
    if not lead:
        return error_response('lead_not_found', status.HTTP_404_NOT_FOUND)
    old_lead_data = copy.deepcopy(lead) 
    
    if is_staff == "true":
        have_modify_all_permission = view_modify_all(auth_id, role_id, LEAD_MODIFY_ALL)
        if str(lead.created_by) != str(auth_id) and not have_modify_all_permission:
            return error_response('permission_denied', status.HTTP_403_FORBIDDEN)
        
    base_payload = {**data, "business_id": business_id}
    lookup_map = {'medium': Medium, 'source': Source, 'tag': Tag, 'team': Team, 'campaign': Campaign}

    # ✅ Bulk lookup validation (reduces DB hits)
    for field, model in lookup_map.items():
        obj_id = base_payload.get(field)
        if obj_id and not model.objects.filter(id=obj_id, business_id=business_id).only('id').exists():
            return error_response(f'{field}_not_found', status.HTTP_404_NOT_FOUND)
    

    contact_serializer = ContactSerializer(instance=lead.contact, data=base_payload)
    if not contact_serializer.is_valid():
        return error_response('record_updation_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, contact_serializer.errors)
    
    with transaction.atomic():
        contact_serializer.save()
        lead_serializer = LeadStoreSerializer(instance=lead, data=base_payload, partial=True)
        if not lead_serializer.is_valid():
            return error_response('record_updation_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, lead_serializer.errors)

        updated_lead = lead_serializer.save()
        attachments = data.get('attachments')
        delete_lead_attachments(business_id, updated_lead.id)
        store_leads_attachments(business_id, [updated_lead], attachments)
        store_leads_tracking([updated_lead], auth_id, old_lead_data)

    return success_response('record_updated', status.HTTP_200_OK, lead_serializer.data)


@api_view(['POST'])
@access_control_middleware
def delete_lead(request, pk):
    data = request.data
    business_id = data.get('auth_business_id')
    auth_id = data.get('auth_id')
    role_id = data.get('auth_role_id')
    is_staff = check_if_user_is_staff(data)

    queryset = __queryset(business_id)
    lead = queryset.filter(id=pk).first()
    if not lead:
        return error_response('lead_not_found', status.HTTP_404_NOT_FOUND)

    if is_staff == "true":
        have_modify_all_permission = view_modify_all(auth_id, role_id, LEAD_MODIFY_ALL)
        if str(lead.created_by) != str(auth_id) and not have_modify_all_permission:
            return error_response('permission_denied', status.HTTP_403_FORBIDDEN)
        
    # child_references = [
    #     {'model': FollowUp, 'foreign_key': 'tag_id'}
    # ]
    # has_refs = has_active_child_references(child_references, pk, business_id)
    # if has_refs:
    #     return error_response("related_tag_record_found_on_deletion", status.HTTP_400_BAD_REQUEST)

    lead.attachments.all().update(deleted_at=timezone.now())
    lead.trackings.all().update(deleted_at=timezone.now())
    lead.delete()
    return success_response('record_deleted', status.HTTP_200_OK)


@api_view(['POST'])
@access_control_middleware
def change_stage(request, pk):
    data = request.data
    business_id = data.get('auth_business_id')
    auth_id = data.get('auth_id')
    role_id = data.get('auth_role_id')
    is_staff = check_if_user_is_staff(data)

    queryset = __queryset(business_id)
    lead = queryset.filter(id=pk).first()
    if not lead:
        return error_response('lead_not_found', status.HTTP_404_NOT_FOUND)

    # Permission check
    if is_staff == "true":
        if str(lead.created_by) != str(auth_id) and not view_modify_all(auth_id, role_id, LEAD_MODIFY_ALL):
            return error_response('permission_denied', status.HTTP_403_FORBIDDEN)

    stage_id = data.get('stage_id')

    stage = Stage.objects.filter(id=stage_id, business_id=business_id).first()
    if not stage:
        return error_response('stage_not_found', status.HTTP_404_NOT_FOUND)

    if lead.stage_id == stage.id:
        return error_response('lead_already_on_same_stage', status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Check if stage requires reason
    stage_reason = None
    if StageReason.objects.filter(stage_id=stage.id, business_id=business_id).exists():
        reason_id = data.get('reason_id')
        stage_reason = StageReason.objects.filter(id=reason_id, stage_id=stage.id, business_id=business_id).first()
        if not stage_reason:
            return error_response('stage_reason_not_found', status.HTTP_404_NOT_FOUND)

    old_lead_data = copy.deepcopy(lead)

    try:
        with transaction.atomic():

            # Create stage reason entry if required
            if stage_reason:
                StageReasonEntry.objects.create(
                    lead_id=lead.id,
                    stage_id=stage.id,
                    stage_reason_id=stage_reason.id,
                    remarks=data.get('remarks'),
                    business_id=business_id,
                    created_by=auth_id
                )

            # Update lead
            lead.stage = stage
            lead.save(update_fields=["stage"])

            # Tracking
            store_leads_tracking([lead], auth_id, old_lead_data)

        return success_response('lead_stage_changed', status.HTTP_200_OK)

    except Exception as e:
        return error_response("lead_stage_change_failed", status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@access_control_middleware
def delete_attachment(request, lead_id, pk):
    data = request.data
    business_id = data.get('auth_business_id')
    try:
        lead_attachment = Attachment.objects.get(id=pk, business_id=business_id, lead_id=lead_id)
        lead_attachment.delete()
        return success_response('record_deleted', status.HTTP_200_OK)
    except Attachment.DoesNotExist:
        return error_response('lead_attachment_not_found', status.HTTP_404_NOT_FOUND)

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

def store_leads_attachments(business_id, leads, attachments):
    if not attachments:
        return

    lead_attachments_object = []

    for lead in leads:
        for attachment in attachments:
            lead_attachments_object.append(
                Attachment(
                    business_id=business_id,
                    lead_id=lead.id,
                    file=attachment
                )
            )

    if lead_attachments_object:
        Attachment.objects.bulk_create(lead_attachments_object)

def store_leads_tracking(leads, auth_id, old_lead=None):
    lead_tracking_objects = []

    # Map lead fields to their tracking model types
    field_mappings = {
        "stage_id": STAGE,
        "source_id": SOURCE,
        "medium_id": MEDIUM,
        "tag_id": TAG,
        "branch_id": BRANCH,
        "session_id": SESSION,
        "assigned_to": ASSIGNED_TO,
        "team_id": TEAM,
        "campaign_id": CAMPAIGN,
    }

    for lead in leads:
        for field_name, model_type in field_mappings.items():
            new_value = getattr(lead, field_name, None)
            old_value = getattr(old_lead, field_name, None) if old_lead else None

            # Track if old_lead is None (new lead) OR value changed
            if new_value and (old_lead is None or old_value != new_value):
                lead_tracking_objects.append(Tracking(
                    business_id=lead.business_id,
                    lead_id=lead.id,
                    model_id=new_value,
                    model_type=model_type,
                    user_id=auth_id
                ))

    # Bulk insert all tracking records
    if lead_tracking_objects:
        Tracking.objects.bulk_create(lead_tracking_objects)


def prepare_leads_to_store(data):
    first_names = data.get("first_names")
    last_names = data.get("last_names")
    date_of_births = data.get("date_of_births")
    contact_numbers = data.get("contact_numbers")
    emails = data.get("emails")
    nics = data.get("nics")
    genders = data.get("genders")

    lead_data_list = []
    iternations = len(first_names)

    for index in range(iternations):
        code = generate_unique_code(Lead)
        lead_data = {
            "business_id": data.get("auth_business_id"),
            "branch_id": data.get("branch_id"),
            "session_id": data.get("session_id"),
            "medium": data.get("medium"),
            "source": data.get("source"),
            "stage": data.get("stage"),
            "tag": data.get("tag"),
            "team": data.get("team"),
            "campaign": data.get("campaign"),
            "contact": data.get("contact"),
            "code": code,
            "first_name": first_names[index] if index < len(first_names) else None,
            "last_name": last_names[index] if index < len(last_names) else None,
            "date_of_birth": date_of_births[index] if index < len(date_of_births) else None,
            "contact_number": contact_numbers[index] if index < len(contact_numbers) else None,
            "email": emails[index] if index < len(emails) else None,
            "nic": nics[index] if index < len(nics) else None,
            "gender": genders[index] if index < len(genders) else None,
            "ethnicity": data.get("ethnicity"),
            "remarks": data.get("remarks"),
            "created_by": data.get("auth_id"),
            "assigned_to": data.get("assigned_to"),
            "priority": data.get("priority", 1),
            "country_id": data.get("country_id"),
            "state_id": data.get("state_id"),
            "city_id": data.get("city_id"),

        }
        lead_data_list.append(lead_data)

    return lead_data_list


def delete_lead_attachments(business_id, lead_id):
    Attachment.objects.filter(business_id=business_id, lead_id=lead_id).delete()