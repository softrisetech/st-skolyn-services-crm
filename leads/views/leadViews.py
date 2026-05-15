import copy
import asyncio
import math
from django.db import transaction
from rest_framework import status
from django.utils import timezone
from django.db import IntegrityError
from rest_framework.decorators import api_view
from report_export.utils.constants import constants
from core.utils.helpers import check_if_user_is_staff
from core.utils.pagination_utils import CustomPagination
from core.utils.helpers import has_active_child_references
from core.utils.decorators import access_control_middleware
from core.utils.date_time_converter import DateTimeConverter

from leads.utils.lead_utils import (
    get_default_lead_stage, 
    get_default_lead_stage_by_priority, 
    generate_unique_code, 
    decrypt_business_id, 
    handle_lead_email_notifications,
    handle_lead_web_notifications,
    get_lead_contact_by_cnic
)
from django.db.models import (
    Q, 
    Case, 
    When, 
    IntegerField
)
from core.utils.response_utils import (
    success_response, 
    error_response
)
from core.utils.notification_utils import (
    notification,
    notification_obj
)
from core.constants.model_constants import (
    STAGE, 
    MEDIUM, 
    SOURCE, 
    TAG, 
    BRANCH, 
    SESSION, 
    ASSIGNED_TO, 
    TEAM, 
    CAMPAIGN, 
    LOST
)
from ..serializers import (
    LeadListSerializer, 
    LeadStoreSerializer, 
    LeadGetSerializer, 
    KanbanLeadSerializer, 
    LeadImportSerializer, 
    ContactSerializer,
    LeadQuickEmailSerializer
)
from access_control.utils.permission_helpers import (
    view_branch_wise, 
    view_modify_all
)
from ..models import (
    Lead, 
    Stage, 
    Source, 
    Medium, 
    Attachment, 
    Tracking, 
    Tag, 
    StageReason, 
    Team, 
    Campaign, 
    StageReasonEntry, 
    FollowUp,
    Contact
)
from access_control.utils.permission_constants import (
    LEAD_VIEW_ALL, 
    LEAD_BRANCH_WISE, 
    LEAD_MODIFY_ALL
)
from leads.utils.filters import (
    filter_by_classes, 
    filter_by_sort_order, 
    filter_by_campaigns, 
    filter_by_teams, 
    filter_by_priority, 
    filter_by_countries, 
    filter_by_states, 
    filter_by_cities, 
    lead_search_filter, 
    filter_by_date_range, 
    filter_by_branches, 
    filter_by_created_by, 
    filter_by_assigned_to, 
    filter_by_mediums, 
    filter_by_sessions, 
    filter_by_sources, 
    filter_by_stages, 
    filter_by_tags
)
from report_export.utils.export_helpers import (
    export_entry, 
    export_obj
)

def __queryset(data, business_id, use_report_db=False):
    filters = {"business_id": business_id}
    is_staff = check_if_user_is_staff(data)
    
    # Choose which DB to use
    db_alias = 'report_connection' if use_report_db else 'default'    
    
    if is_staff in ["true", True]:
        user_id = data.get('auth_id')
        role_id = data.get('auth_role_id')
        view_all = LEAD_VIEW_ALL
        branch_wise = LEAD_BRANCH_WISE
        have_view_all_permission = view_modify_all(user_id, role_id, view_all)
        have_branch_wise_permission = view_branch_wise(user_id, role_id, branch_wise)
        queryset = Lead.objects.using(db_alias).filter(**filters)

        if not have_view_all_permission:
            queryset = queryset.filter(Q(created_by=user_id) | Q(assigned_to=user_id))

        if have_branch_wise_permission:
            branch_id = data.get("auth_branch_id")
            queryset = queryset.filter(branch_id=branch_id)

        return queryset

    return Lead.objects.using(db_alias).filter(**filters)


def __apply_filters(queryset, filters):
    queryset = lead_search_filter(queryset, filters)
    queryset = filter_by_branches(queryset, filters)
    queryset = filter_by_sessions(queryset, filters)
    queryset = filter_by_classes(queryset, filters)
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
    queryset = __queryset(data, business_id)
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
    user_timezone = data.get("auth_timezone")
    contact_id = data.get('contact_id', None)
    base_payload = {**data, "business_id": business_id, "created_by": auth_id}
    lookup_map = {'medium': Medium, 'source': Source, 'tag': Tag, 'team': Team, 'campaign': Campaign}
    web_notifications, email_notifications, other = [], [], {}


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

    # if contact id given in request
    if contact_id:
        contact = Contact.objects.filter(business_id=business_id, id=contact_id).first()
        if not contact:
            return error_response('contact_not_found', status.HTTP_404_NOT_FOUND)
    # if contact id not given in request
    else:
        # check for contact already exists in system by father and mother cnic 
        existing_contact = get_lead_contact_by_cnic(business_id, base_payload.get("father_nic"), base_payload.get("mother_nic"))
        if existing_contact:
            contact_id = existing_contact.id

        # if contact not exists in system create new contact
        if contact_id is None:
            # ✅ Validate Contact BEFORE transaction
            contact_serializer = ContactSerializer(data=base_payload)
            if not contact_serializer.is_valid():
                return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, contact_serializer.errors)

    with transaction.atomic():
        if contact_id is None:
            contact = contact_serializer.save()
            contact_id = contact.id

        leads_payload = prepare_leads_to_store({**base_payload, "contact": contact_id})
        lead_serializer = LeadStoreSerializer(data=leads_payload, many=True)
        if not lead_serializer.is_valid():
            return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, lead_serializer.errors)

        leads = lead_serializer.save()
        attachments = data.get('attachments')
        store_leads_attachments(business_id, leads, attachments)
        store_leads_tracking(leads, auth_id)

        single_lead = leads[0] if leads else None
        if single_lead:
            email_notifications = handle_lead_email_notifications(data, user_timezone, ["parent_email", "team_lead"], email_notifications, "lead_created", single_lead)


        for lead in leads:
            email_notifications = handle_lead_email_notifications(data, user_timezone, ["assigned_to"], email_notifications, "lead_assigned", lead)
            web_notifications = handle_lead_web_notifications(data, user_timezone, ["team_lead"], web_notifications, "lead_created", lead)
            web_notifications = handle_lead_web_notifications(data, user_timezone, ["assigned_to"], web_notifications, "lead_assigned", lead)

        other['notification'] = notification(email_notifications, web_notifications)

    return success_response('record_stored', status.HTTP_201_CREATED, lead_serializer.data, other)

@api_view(['POST'])
@access_control_middleware
def get_lead(request, pk):
    data = request.data
    business_id = data.get('auth_business_id')
    userTimezone = data.get("auth_timezone")
    queryset = __queryset(data, business_id)
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
    contact_id = data.get('contact_id')
    data["contact"] = contact_id
    is_staff = check_if_user_is_staff(data)
    user_timezone = data.get("auth_timezone")
    web_notifications, email_notifications, other = [], [], {}


    queryset = __queryset(data, business_id)
    lead = queryset.filter(id=pk).first()
    if not lead:
        return error_response('lead_not_found', status.HTTP_404_NOT_FOUND)
    old_lead_data = copy.deepcopy(lead) 
    
    if is_staff in ["true", True]:
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
        
    contact = Contact.objects.filter(business_id=business_id, id=contact_id).first()
    if not contact:
        return error_response('contact_not_found', status.HTTP_404_NOT_FOUND)

    
    with transaction.atomic():
        lead_serializer = LeadStoreSerializer(instance=lead, data=base_payload, partial=True)
        if not lead_serializer.is_valid():
            return error_response('record_updation_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, lead_serializer.errors)

        updated_lead = lead_serializer.save()
        attachments = data.get('attachments')
        delete_lead_attachments(business_id, updated_lead.id)
        store_leads_attachments(business_id, [updated_lead], attachments)
        store_leads_tracking([updated_lead], auth_id, old_lead_data)

        if old_lead_data.assigned_to != updated_lead.assigned_to:
            email_notifications = handle_lead_email_notifications(data, user_timezone, ["assigned_to", "last_activity"], email_notifications, "lead_assigned", lead)
            web_notifications = handle_lead_web_notifications(data, user_timezone, ["assigned_to", "last_activity"], web_notifications, "lead_assigned", lead)
        
        other['notification'] = notification(email_notifications, web_notifications)
        

    return success_response('record_updated', status.HTTP_200_OK, lead_serializer.data, other)


@api_view(['POST'])
@access_control_middleware
def delete_lead(request, pk):
    data = request.data
    business_id = data.get('auth_business_id')
    auth_id = data.get('auth_id')
    role_id = data.get('auth_role_id')
    is_staff = check_if_user_is_staff(data)

    queryset = __queryset(data, business_id)
    lead = queryset.filter(id=pk).first()
    if not lead:
        return error_response('lead_not_found', status.HTTP_404_NOT_FOUND)

    if is_staff in ["true", True]:
        have_modify_all_permission = view_modify_all(auth_id, role_id, LEAD_MODIFY_ALL)
        if str(lead.created_by) != str(auth_id) and not have_modify_all_permission:
            return error_response('permission_denied', status.HTTP_403_FORBIDDEN)
        
    child_references = [
        {'model': FollowUp, 'foreign_key': 'lead_id'}
    ]
    has_refs = has_active_child_references(child_references, pk, business_id)
    if has_refs:
        return error_response("related_tag_record_found_on_deletion", status.HTTP_400_BAD_REQUEST)

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
    remarks = data.get('remarks')
    user_timezone = data.get("auth_timezone")
    web_notifications, email_notifications, other = [], [], {}

    queryset = __queryset(data, business_id)
    lead = queryset.filter(id=pk).first()
    if not lead:
        return error_response('lead_not_found', status.HTTP_404_NOT_FOUND)

    # Permission check
    if is_staff in ["true", True]:
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
    if StageReason.objects.filter(stage_id=stage.id, business_id=business_id, is_active=True).exists():
        reason_id = data.get('reason_id')
        stage_reason = StageReason.objects.filter(id=reason_id, stage_id=stage.id, business_id=business_id, is_active=True).first()
        if not stage_reason:
            return error_response('stage_reason_not_found', status.HTTP_404_NOT_FOUND)

    old_lead_data = copy.deepcopy(lead)

    try:
        with transaction.atomic():
            
            stage_reason_entry = None
            # Create stage reason entry if required
            if stage_reason:
                stage_reason_entry = StageReasonEntry.objects.create(
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
            store_leads_tracking([lead], auth_id, old_lead_data, stage_reason_entry)


            template = None
            if stage.type == LOST:
                template = "lead_lost"
            elif stage.type == "won":
                template = "lead_won"

            if template:
                email_notifications = handle_lead_email_notifications(data, user_timezone, ["team_lead", "assigned_to", "parent_email"], email_notifications, template, lead, stage_reason, remarks)
                web_notifications = handle_lead_web_notifications(data, user_timezone, ["team_lead", "assigned_to", "parent_email"], web_notifications, template, lead, stage_reason, remarks)

            email_notifications = handle_lead_email_notifications(data, user_timezone, ["parent_email"], email_notifications, "parent_trigger_email", lead, stage_reason, remarks)
            other['notification'] = notification(email_notifications, web_notifications)

        return success_response('lead_stage_changed', status.HTTP_200_OK, [], other)

    except Exception as e:
        return error_response("lead_stage_change_failed", status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))
    

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
    

@api_view(['POST'])
@access_control_middleware
def get_leads_kanban(request, stage_id=None):
    data = request.data
    business_id = data.get('auth_business_id')
    queryset = __queryset(data, business_id)
    #Get pagination params
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    skip = (page - 1) * page_size
    take = skip + page_size

    if stage_id:
        stage_leads = queryset.filter(stage=stage_id)[skip:take]
        serialized_data = KanbanLeadSerializer(stage_leads, many=True).data
        data = {
                "items": serialized_data,
                "pagination": {
                "page": page,
                "page_size": page_size,
                "all_items_count": queryset.filter(stage=stage_id).count(),
                "total_pages": math.ceil(queryset.filter(stage=stage_id).count()/page_size),
                "remaining_items_count": max(queryset.filter(stage=stage_id).count() - (page_size * page), 0)
            }
        }
        return success_response('record_fetched', status.HTTP_200_OK, data)

    queryset = __apply_filters(queryset, data)
    stages = Stage.objects.filter(business_id=business_id, is_active=1).order_by(
        Case(
            When(type="open", then=0),
            When(type="won", then=1),
            When(type="lost", then=2),
            default=3,
            output_field=IntegerField(),
        ),
        "priority"
    )

    grouped_leads = {"stages": []}
    for stage in stages:
        stage_leads = queryset.filter(stage=stage.id)[skip:take]  # Apply Skip-Take (Offset-Limit)
        serialized_data = KanbanLeadSerializer(stage_leads, many=True).data
        total_items = queryset.filter(stage=stage.id).count()

        grouped_leads["stages"].append({  # Append each stage's data to the list
            "id": stage.id,
            "name": stage.name,
            "type": stage.type,
            "items": serialized_data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "all_items_count": total_items,
                "total_pages": math.ceil(total_items / page_size),
                "remaining_items_count": max(total_items - skip - page_size, 0)
            }
        })
    return success_response('record_fetched', status.HTTP_200_OK, grouped_leads)


@api_view(['POST'])
def generate_leads(request):
    data = request.data.copy()
    business_id = data.get('encrypted_business_id')
    source = data.get('source')

    business_id = decrypt_business_id(business_id)
    source = Source.objects.filter(name__iexact=source, business_id=business_id).first()
    if not source:
        return error_response('source_not_found', status.HTTP_404_NOT_FOUND)
    
    data["source"] = source.id
    
    # ✅ Single optimized stage fetch
    default_stage = (get_default_lead_stage(business_id) or get_default_lead_stage_by_priority(business_id))
    if not default_stage:
        return error_response('default_stage_missing', status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    data["stage"] = default_stage.id

    # ✅ Validate Contact BEFORE transaction
    contact_serializer = ContactSerializer(data=data)
    if not contact_serializer.is_valid():
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, contact_serializer.errors)
    
    with transaction.atomic():
        contact = contact_serializer.save()
        leads_payload = prepare_leads_to_store({**data, "contact": contact.id})
        lead_serializer = LeadStoreSerializer(data=leads_payload, many=True)
        if not lead_serializer.is_valid():
            return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, lead_serializer.errors)

        lead_serializer.save()

    return success_response('record_stored', status.HTTP_201_CREATED, lead_serializer.data)


# Import Leads Function
@api_view(['POST'])
@access_control_middleware
def import_leads(request):
    data = request.data
    business_id = data.get('auth_business_id')
    user_timezone = data.get("auth_timezone")
    branch_id = data.get('branch_id')
    auth_id = data.get('auth_id')
    leads_data = data.get('leads', [])
    row_offset = data.get('row_offset', 2)

    file_errors = []

    # =============================
    # ✅ Step 1: Bulk fetch reference data
    # =============================
    mediums = dict(
        Medium.objects.filter(business_id=business_id).values_list("name", "id")
    )
    sources = dict(
        Source.objects.filter(business_id=business_id).values_list("name", "id")
    )
    tags = dict(
        Tag.objects.filter(business_id=business_id).values_list("name", "id")
    )

    # =============================
    # ✅ Step 2: Prepare Contacts + Leads
    # =============================
    contacts_to_create = []
    leads_to_create = []

    for idx, lead_data in enumerate(leads_data):
        actual_row = row_offset + idx

        try:
            medium_id = mediums.get(lead_data.get('medium'))
            source_id = sources.get(lead_data.get('source'))
            tag_id = tags.get(lead_data.get('tag'))

            stage_obj = (
                get_default_lead_stage(business_id) or
                get_default_lead_stage_by_priority(business_id)
            )

            created_at = DateTimeConverter.to_utc_datetime(
                lead_data.get("created_at") or timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_timezone
            )

            # -------------------------
            # ✅ CONTACT PREPARATION
            # -------------------------
            contact_payload = {
                "business_id": business_id,
                "father_first_name": lead_data.get("father_first_name"),
                "father_last_name": lead_data.get("father_last_name"),
                "father_contact_number": lead_data.get("father_contact_number"),
                "father_email": lead_data.get("father_email"),
                "father_nic": lead_data.get("father_nic"),
                "is_father_applicable": lead_data.get("is_father_applicable", False),

                "mother_first_name": lead_data.get("mother_first_name"),
                "mother_last_name": lead_data.get("mother_last_name"),
                "mother_contact_number": lead_data.get("mother_contact_number"),
                "mother_email": lead_data.get("mother_email"),
                "mother_nic": lead_data.get("mother_nic"),
                "is_mother_applicable": lead_data.get("is_mother_applicable", False),

                "created_at": created_at,
                "updated_at": created_at,
            }

            contact_serializer = ContactSerializer(data=contact_payload)

            if not contact_serializer.is_valid():
                file_errors.append({
                    "row": actual_row,
                    "errors": contact_serializer.errors
                })
                continue

            contacts_to_create.append(Contact(**contact_serializer.validated_data))

            # -------------------------
            # ✅ LEAD PREPARATION
            # -------------------------
            prepared_lead = {
                "business_id": business_id,
                "branch_id": branch_id,
                "medium": medium_id,
                "source": source_id,
                "stage": stage_obj.id if stage_obj else None,
                "tag": tag_id,
                "first_name": lead_data.get("first_name"),
                "last_name": lead_data.get("last_name"),
                "date_of_birth": lead_data.get("date_of_birth"),
                "contact_number": lead_data.get("contact_number"),
                "email": lead_data.get("email"),
                "nic": lead_data.get("nic"),
                "gender": lead_data.get("gender"),
                "remarks": lead_data.get("remarks"),
                "created_at": created_at,
                "updated_at": created_at,
                "created_by": auth_id,
                "priority": 1,
                "is_imported": True,
                "imported_at": DateTimeConverter.to_utc_datetime(
                    timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                    user_timezone
                ),
            }

            serializer = LeadImportSerializer(data=prepared_lead)

            if serializer.is_valid():
                leads_to_create.append(serializer.validated_data)
            else:
                file_errors.append({
                    "row": actual_row,
                    "errors": serializer.errors
                })

        except Exception as e:
            file_errors.append({
                "row": actual_row,
                "errors": {"internal": str(e)}
            })

    # =============================
    # ✅ Step 3: Return validation errors
    # =============================
    if file_errors:
        return error_response(
            'import_file_data_not_correct',
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {"file_errors": file_errors}
        )

    # =============================
    # ✅ Step 4: Bulk Create (Atomic)
    # =============================
    try:
        with transaction.atomic():

            # 🔹 Create Contacts
            created_contacts = Contact.objects.bulk_create(contacts_to_create)

            # 🔹 Map contact_id → leads
            final_leads = []
            for i, lead_data in enumerate(leads_to_create):
                lead_data["contact_id"] = created_contacts[i].id
                final_leads.append(Lead(**lead_data))

            # 🔹 Create Leads
            imported_leads = Lead.objects.bulk_create(final_leads)

            store_leads_tracking(imported_leads, auth_id)

        return success_response(
            'leads_imported',
            status.HTTP_201_CREATED,
            {'message': 'Leads successfully imported.'}
        )

    except IntegrityError:
        return error_response(
            'import_file_data_not_correct',
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {"file_errors": [{
                "row": None,
                "errors": {"database": "Duplicate or invalid data detected."}
            }]}
        )

    except Exception as e:
        return error_response(
            'internal_server_error',
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            str(e)
        )
    

@api_view(["POST"])
def validate_import_leads(request):
    data = request.data
    business_id = data.get('auth_business_id')
    user_timezone = data.get("auth_timezone")
    branch_id = data.get('branch_id')
    auth_id = data.get('auth_id')
    leads_data = data.get('leads', [])
    row_offset = data.get('row_offset', 2)

    file_errors = []

    # --- Bulk fetch reference data ---
    mediums = dict(
        Medium.objects.filter(business_id=business_id).values_list("name", "id")
    )
    sources = dict(
        Source.objects.filter(business_id=business_id).values_list("name", "id")
    )
    tags = dict(
        Tag.objects.filter(business_id=business_id).values_list("name", "id")
    )

    # --- Validate all rows ---
    for idx, lead_data in enumerate(leads_data):
        actual_row = row_offset + idx
        row_errors = {}

        try:
            # --- Step 1: Validate reference fields ---
            if lead_data.get('medium') and lead_data['medium'] not in mediums:
                row_errors['medium'] = [f"Medium '{lead_data['medium']}' does not exist."]

            if lead_data.get('source') and lead_data['source'] not in sources:
                row_errors['source'] = [f"Source '{lead_data['source']}' does not exist."]

            if lead_data.get('tag') and lead_data['tag'] not in tags:
                row_errors['tag'] = [f"Tag '{lead_data['tag']}' does not exist."]

            # --- Step 2: Prepare data for serializer ---
            medium_id = mediums.get(lead_data.get('medium'))
            source_id = sources.get(lead_data.get('source'))
            tag_id = tags.get(lead_data.get('tag'))

            stage_obj = (
                get_default_lead_stage(business_id) or
                get_default_lead_stage_by_priority(business_id)
            )

            created_at = DateTimeConverter.to_utc_datetime(
                lead_data.get("created_at") or timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                user_timezone
            )

            prepared_lead = {
                "business_id": business_id,
                "branch_id": branch_id,
                "medium": medium_id,
                "source": source_id,
                "stage": stage_obj.id if stage_obj else None,
                "tag": tag_id,
                "first_name": lead_data.get("first_name"),
                "last_name": lead_data.get("last_name"),
                "date_of_birth": lead_data.get("date_of_birth"),
                "contact_number": lead_data.get("contact_number"),
                "email": lead_data.get("email"),
                "nic": lead_data.get("nic"),
                "gender": lead_data.get("gender"),
                "remarks": lead_data.get("remarks"),
                "created_at": created_at,
                "updated_at": created_at,
                "created_by": auth_id,
                "priority": 1,
                "is_imported": True,
                "imported_at": DateTimeConverter.to_utc_datetime(
                    timezone.now().strftime("%Y-%m-%d %H:%M:%S"), user_timezone
                ),
            }

            # --- Step 3: Serializer validation ---
            serializer = LeadImportSerializer(data=prepared_lead)

            if not serializer.is_valid():
                for field, messages in serializer.errors.items():
                    row_errors[field] = [str(msg) for msg in messages]

        except Exception as e:
            row_errors['internal'] = [str(e)]

        # --- Collect row errors ---
        if row_errors:
            file_errors.append({
                "row": actual_row,
                "errors": row_errors
            })

    # --- Final response ---
    if file_errors:
        return error_response(
            'import_file_data_not_correct',
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {"file_errors": file_errors}
        )

    return success_response(
        'validation_successful',
        status.HTTP_200_OK,
        {'message': 'All leads are valid.'}
    )


@api_view(["POST"])
def send_quick_email(request):
    data = request.data.copy()
    data["business_id"] = data.get("auth_business_id")
    other = {}
    serializer = LeadQuickEmailSerializer(data=data)
    if not serializer.is_valid():
        return error_response('record_store_failed', status.HTTP_422_UNPROCESSABLE_ENTITY, serializer.errors)
    serializer.save()

    other['notification'] = notification(notification_obj(
        "send_lead_quick_email",
        data["recipients"],
        {
            "business_id": data["business_id"],
            "subject": data["subject"],
            "message": data["message"]
        }

    ))

    return success_response('lead_quick_email_send', status.HTTP_201_CREATED, [], other)





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

def store_leads_tracking(leads, auth_id, old_lead=None, stage_reason_entry=None):
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
                    user_id=auth_id,
                    stage_reason_entry_id=stage_reason_entry.id if model_type == "stage" and stage_reason_entry else None
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
    ethnicities = data.get("ethnicities")


    lead_data_list = []
    iternations = len(first_names)

    for index in range(iternations):
        code = generate_unique_code(Lead)
        lead_data = {
            "business_id": data.get("auth_business_id"),
            "branch_id": data.get("branch_id"),
            "session_id": data.get("session_id"),
            "class_id": data.get("class_id"),
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
            "ethnicity": ethnicities[index] if index < len(ethnicities) else None,
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