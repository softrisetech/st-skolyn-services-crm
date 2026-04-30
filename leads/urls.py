from django.urls import path
from .views.followUpViews import (
    get_lead_follow_ups, 
    get_lead_follow_up, 
    store_lead_follow_up, 
    update_lead_follow_up, 
    delete_lead_follow_up
)
from .views.trackingViews import (
    get_lead_trackings
)
from .views.tagViews import (
    get_lead_tags, 
    get_lead_tag, 
    store_lead_tag, 
    update_lead_tag, 
    delete_lead_tag
)
from .views.mediumViews import (
    get_lead_mediums, 
    get_lead_medium, 
    store_lead_medium, 
    update_lead_medium, 
    delete_lead_medium
)
from .views.sourceViews import (
    get_lead_sources, 
    get_lead_source, 
    store_lead_source, 
    update_lead_source, 
    delete_lead_source
)
from .views.followUpTypeViews import (
    get_lead_follow_up_types, 
    get_lead_follow_up_type, 
    store_lead_follow_up_type, 
    update_lead_follow_up_type, 
    delete_lead_follow_up_type
)
from .views.stageViews import (
    get_lead_stages, 
    get_lead_stage, 
    store_lead_stage, 
    update_lead_stage, 
    delete_lead_stage,
    create_default_stages
)
from .views.dashboardViews import (
    get_leads_summary, 
    get_leads_funnel,
    get_sources_leads,
    get_mediums_leads,
    get_campaigns_leads,
    get_assigned_leads,
    get_lost_leads_by_reason,
    get_leads_conversion_trend
)
from .views.leadViews import (
    get_leads_kanban, 
    get_leads, 
    store_lead, 
    get_lead, 
    update_lead, 
    delete_lead, 
    change_stage, 
    delete_attachment,
    generate_leads,
    export_leads,
    import_leads,
    validate_import_leads,
    send_quick_email
)
from .views.stageReasonViews import (
    get_stage_reasons, 
    get_stage_reason, 
    store_stage_reason, 
    update_stage_reason, 
    delete_stage_reason
)
from .views.campaignViews import (
    get_lead_campaigns, 
    get_lead_campaign, 
    store_lead_campaign, 
    update_lead_campaign, 
    delete_lead_campaign
)
from .views.teamViews import (
    get_lead_teams, 
    get_lead_team, 
    store_lead_team, 
    update_lead_team, 
    delete_lead_team
)
from .views.contactViews import (
    get_lead_contacts, 
    get_lead_contact, 
    store_lead_contact, 
    update_lead_contact, 
    delete_lead_contact
)
from .views.instituteViews import (
    get_lead_institutes, 
    get_lead_institute, 
    store_lead_institute, 
    update_lead_institute, 
    delete_lead_institute
)
from .views.preRequisiteViews import (
    get_lead_pre_requisites, 
    store_lead_pre_requisite, 
    update_lead_pre_requisite, 
    delete_lead_pre_requisite
)

from .views.sessionTargetViews import (
    get_lead_session_targets, 
    get_lead_session_target, 
    store_lead_session_target, 
    update_lead_session_target, 
    delete_lead_session_target
)

from .reports.crm_reports import *
from .reports.crm_report_exports import *

urlpatterns = [

    path('dashboard/leads/summary', get_leads_summary),
    path('dashboard/leads/funnel', get_leads_funnel),
    path('dashboard/sources/leads', get_sources_leads),
    path('dashboard/mediums/leads', get_mediums_leads),
    path('dashboard/campaigns/leads', get_campaigns_leads),
    path('dashboard/assigned/leads', get_assigned_leads),
    path('dashboard/lost/reason/leads', get_lost_leads_by_reason),
    path('dashboard/leads/conversion/trend', get_leads_conversion_trend),
    
    path('reports/high-priority-no-followup', get_high_priority_no_followup_leads),
    path('reports/no-followup-leads', get_no_followup_leads),
    path('reports/upcoming-followups', get_upcoming_followup_leads),
    path('reports/overdue-followups', get_overdue_followup_leads),
    path('reports/lost-leads', get_lost_leads),
    
    # Exports
    
    path('reports/export/high-priority-no-followup/', export_high_priority_no_followup),
    path('reports/export/no-followup-leads/', export_no_followup_leads),
    path('reports/export/upcoming-followups/', export_upcoming_followup_leads),
    path('reports/export/overdue-followups/', export_overdue_followup_leads),
    path('reports/export/lost-leads/', export_lost_leads),


    path('mediums/list', get_lead_mediums),
    path('mediums/<uuid:pk>/get', get_lead_medium),
    path('mediums/store', store_lead_medium),
    path('mediums/<uuid:pk>/update', update_lead_medium),
    path('mediums/<uuid:pk>/delete', delete_lead_medium),

    path('sources/list', get_lead_sources),
    path('sources/<uuid:pk>/get', get_lead_source),
    path('sources/store', store_lead_source),
    path('sources/<uuid:pk>/update', update_lead_source),
    path('sources/<uuid:pk>/delete', delete_lead_source),

    path('stages/list', get_lead_stages),
    path('stages/<uuid:pk>/get', get_lead_stage),
    path('stages/store', store_lead_stage),
    path('stages/<uuid:pk>/update', update_lead_stage),
    path('stages/<uuid:pk>/delete', delete_lead_stage),
    path('stages/create/default', create_default_stages),


    path('stages/reasons/list', get_stage_reasons),
    path('stages/reasons/<uuid:pk>/get', get_stage_reason),
    path('stages/reasons/store', store_stage_reason),
    path('stages/reasons/<uuid:pk>/update', update_stage_reason),
    path('stages/reasons/<uuid:pk>/delete', delete_stage_reason),

    path('tags/list', get_lead_tags),
    path('tags/<uuid:pk>/get', get_lead_tag),
    path('tags/store', store_lead_tag),
    path('tags/<uuid:pk>/update', update_lead_tag),
    path('tags/<uuid:pk>/delete', delete_lead_tag),

    path('institutes/list', get_lead_institutes),
    path('institutes/<uuid:pk>/get', get_lead_institute),
    path('institutes/store', store_lead_institute),
    path('institutes/<uuid:pk>/update', update_lead_institute),
    path('institutes/<uuid:pk>/delete', delete_lead_institute),

    path('campaigns/list', get_lead_campaigns),
    path('campaigns/<uuid:pk>/get', get_lead_campaign),
    path('campaigns/store', store_lead_campaign),
    path('campaigns/<uuid:pk>/update', update_lead_campaign),
    path('campaigns/<uuid:pk>/delete', delete_lead_campaign),

    path('follow-up/types/list', get_lead_follow_up_types),
    path('follow-up/types/<uuid:pk>/get', get_lead_follow_up_type),
    path('follow-up/types/store', store_lead_follow_up_type),
    path('follow-up/types/<uuid:pk>/update', update_lead_follow_up_type),
    path('follow-up/types/<uuid:pk>/delete', delete_lead_follow_up_type),


    path('teams/list', get_lead_teams),
    path('teams/<uuid:pk>/get', get_lead_team),
    path('teams/store', store_lead_team),
    path('teams/<uuid:pk>/update', update_lead_team),
    path('teams/<uuid:pk>/delete', delete_lead_team),

    path('session/targets/list', get_lead_session_targets),
    path('session/targets/<uuid:pk>/get', get_lead_session_target),
    path('session/targets/store', store_lead_session_target),
    path('session/targets/<uuid:pk>/update', update_lead_session_target),
    path('session/targets/<uuid:pk>/delete', delete_lead_session_target),

    path('leads/list', get_leads),
    path('leads/export/', export_leads, name='lead-export'),
    path('leads/<uuid:pk>/get', get_lead),
    path('leads/store', store_lead),
    path('leads/<uuid:pk>/update', update_lead),
    path('leads/<uuid:pk>/delete', delete_lead),
    path('leads/<uuid:pk>/change/stage', change_stage),
    path('leads/<uuid:lead_id>/attachment/<uuid:pk>/delete', delete_attachment),
    path('leads/kanban', get_leads_kanban),
    path('leads/kanban/<uuid:stage_id>', get_leads_kanban),
    path('leads/generate', generate_leads),
    path('leads/import', import_leads),
    path('leads/validate/import', validate_import_leads),
    path('leads/quick/email', send_quick_email),



    path('lead/<uuid:lead_id>/follow-ups/list', get_lead_follow_ups),
    path('lead/<uuid:lead_id>/follow-ups/<uuid:pk>/get', get_lead_follow_up),
    path('lead/<uuid:lead_id>/follow-ups/store', store_lead_follow_up),
    path('lead/<uuid:lead_id>/follow-ups/<uuid:pk>/update', update_lead_follow_up),
    path('lead/<uuid:lead_id>/follow-ups/<uuid:pk>/delete', delete_lead_follow_up),
    

    path('lead/<uuid:lead_id>/pre-requisites/list', get_lead_pre_requisites),
    path('lead/<uuid:lead_id>/pre-requisites/store', store_lead_pre_requisite),
    path('lead/<uuid:lead_id>/pre-requisites/<uuid:pk>/update', update_lead_pre_requisite),
    path('lead/<uuid:lead_id>/pre-requisites/<uuid:pk>/delete', delete_lead_pre_requisite),

    path('contacts/list', get_lead_contacts),
    path('contacts/<uuid:pk>/get', get_lead_contact),
    path('contacts/store', store_lead_contact),
    path('contacts/<uuid:pk>/update', update_lead_contact),
    path('contacts/<uuid:pk>/delete', delete_lead_contact),

    path('lead/trackings/list', get_lead_trackings),

]
