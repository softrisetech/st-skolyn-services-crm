from django.urls import path
from .views.followUpViews import get_lead_follow_ups, get_lead_follow_up, store_lead_follow_up, update_lead_follow_up, delete_lead_follow_up
from .views.trackingViews import get_lead_trackings
from .views.tagViews import get_lead_tags, get_lead_tag, store_lead_tag, update_lead_tag, delete_lead_tag
from .views.mediumViews import get_lead_mediums, get_lead_medium, store_lead_medium, update_lead_medium, delete_lead_medium
from .views.sourceViews import get_lead_sources, get_lead_source, store_lead_source, update_lead_source, delete_lead_source
from .views.followUpTypeViews import get_lead_follow_up_types, get_lead_follow_up_type, store_lead_follow_up_type, update_lead_follow_up_type, delete_lead_follow_up_type
from .views.stageViews import get_lead_stages, get_lead_stage, store_lead_stage, update_lead_stage, delete_lead_stage
from .views.dashboardViews import leads_by_source, leads_by_medium, leads_by_stage, funnel_stages, leads_by_tag, leads_by_branch, leads_by_session, monthly_leads
from .views.leadViews import get_leads, store_lead, get_lead, update_lead, delete_lead, change_stage, delete_attachment
from .views.stageReasonViews import get_stage_reasons, get_stage_reason, store_stage_reason, update_stage_reason, delete_stage_reason
from .views.campaignViews import get_lead_campaigns, get_lead_campaign, store_lead_campaign, update_lead_campaign, delete_lead_campaign
from .views.teamViews import get_lead_teams, get_lead_team, store_lead_team, update_lead_team, delete_lead_team
from .views.contactViews import get_lead_contacts, get_lead_contact, store_lead_contact, update_lead_contact, delete_lead_contact
from .views.instituteViews import get_lead_institutes, get_lead_institute, store_lead_institute, update_lead_institute, delete_lead_institute
from .views.preRequisiteViews import get_lead_pre_requisites, store_lead_pre_requisite, update_lead_pre_requisite, delete_lead_pre_requisite

urlpatterns = [

    path('lead/mediums/list', get_lead_mediums),
    path('lead/mediums/<uuid:pk>/get', get_lead_medium),
    path('lead/mediums/store', store_lead_medium),
    path('lead/mediums/<uuid:pk>/update', update_lead_medium),
    path('lead/mediums/<uuid:pk>/delete', delete_lead_medium),

    path('lead/sources/list', get_lead_sources),
    path('lead/sources/<uuid:pk>/get', get_lead_source),
    path('lead/sources/store', store_lead_source),
    path('lead/sources/<uuid:pk>/update', update_lead_source),
    path('lead/sources/<uuid:pk>/delete', delete_lead_source),

    path('lead/stages/list', get_lead_stages),
    path('lead/stages/<uuid:pk>/get', get_lead_stage),
    path('lead/stages/store', store_lead_stage),
    path('lead/stages/<uuid:pk>/update', update_lead_stage),
    path('lead/stages/<uuid:pk>/delete', delete_lead_stage),

    path('lead/stages/reasons/list', get_stage_reasons),
    path('lead/stages/reasons/<uuid:pk>/get', get_stage_reason),
    path('lead/stages/reasons/store', store_stage_reason),
    path('lead/stages/reasons/<uuid:pk>/update', update_stage_reason),
    path('lead/stages/reasons/<uuid:pk>/delete', delete_stage_reason),

    path('lead/tags/list', get_lead_tags),
    path('lead/tags/<uuid:pk>/get', get_lead_tag),
    path('lead/tags/store', store_lead_tag),
    path('lead/tags/<uuid:pk>/update', update_lead_tag),
    path('lead/tags/<uuid:pk>/delete', delete_lead_tag),

    path('lead/institutes/list', get_lead_institutes),
    path('lead/institutes/<uuid:pk>/get', get_lead_institute),
    path('lead/institutes/store', store_lead_institute),
    path('lead/institutes/<uuid:pk>/update', update_lead_institute),
    path('lead/institutes/<uuid:pk>/delete', delete_lead_institute),

    path('lead/campaigns/list', get_lead_campaigns),
    path('lead/campaigns/<uuid:pk>/get', get_lead_campaign),
    path('lead/campaigns/store', store_lead_campaign),
    path('lead/campaigns/<uuid:pk>/update', update_lead_campaign),
    path('lead/campaigns/<uuid:pk>/delete', delete_lead_campaign),

    path('lead/follow-up/types/list', get_lead_follow_up_types),
    path('lead/follow-up/types/<uuid:pk>/get', get_lead_follow_up_type),
    path('lead/follow-up/types/store', store_lead_follow_up_type),
    path('lead/follow-up/types/<uuid:pk>/update', update_lead_follow_up_type),
    path('lead/follow-up/types/<uuid:pk>/delete', delete_lead_follow_up_type),


    path('lead/teams/list', get_lead_teams),
    path('lead/teams/<uuid:pk>/get', get_lead_team),
    path('lead/teams/store', store_lead_team),
    path('lead/teams/<uuid:pk>/update', update_lead_team),
    path('lead/teams/<uuid:pk>/delete', delete_lead_team),

    path('leads/list', get_leads),
    path('leads/<uuid:pk>/get', get_lead),
    path('leads/store', store_lead),
    path('leads/<uuid:pk>/update', update_lead),
    path('leads/<uuid:pk>/delete', delete_lead),
    path('leads/<uuid:pk>/change/stage', change_stage),
    path('leads/<uuid:lead_id>/attachment/<uuid:pk>/delete', delete_attachment),

    path('lead/<uuid:lead_id>/follow-ups/list', get_lead_follow_ups),
    path('lead/<uuid:lead_id>/follow-ups/<uuid:pk>/get', get_lead_follow_up),
    path('lead/<uuid:lead_id>/follow-ups/store', store_lead_follow_up),
    path('lead/<uuid:lead_id>/follow-ups/<uuid:pk>/update', update_lead_follow_up),
    path('lead/<uuid:lead_id>/follow-ups/<uuid:pk>/delete', delete_lead_follow_up),

    path('lead/<uuid:lead_id>/pre-requisites/list', get_lead_pre_requisites),
    path('lead/<uuid:lead_id>/pre-requisites/store', store_lead_pre_requisite),
    path('lead/<uuid:lead_id>/pre-requisites/<uuid:pk>/update', update_lead_pre_requisite),
    path('lead/<uuid:lead_id>/pre-requisites/<uuid:pk>/delete', delete_lead_pre_requisite),

    path('lead/contacts/list', get_lead_contacts),
    path('lead/contacts/<uuid:pk>/get', get_lead_contact),
    path('lead/contacts/store', store_lead_contact),
    path('lead/contacts/<uuid:pk>/update', update_lead_contact),
    path('lead/contacts/<uuid:pk>/delete', delete_lead_contact),

    path('lead/trackings/list', get_lead_trackings),

    # path('leads/', lead_list),
    # path('leads/stage-wise/', lead_list_stage_wise),
    # path('leads/stage-wise/<uuid:pk>/', lead_list_stage_wise),
    # path('leads/import/', import_leads),
    # path('leads/export/', export_leads),
    # path('leads/<uuid:pk>/', lead_list),
    # path('leads/create/', lead_create),
    # path('leads/update/<uuid:pk>/', lead_update),
    # path('leads/delete/<uuid:pk>/', lead_delete),
    # path('leads/change/stage/<uuid:pk>/', lead_change_stage),
    # path('leads/attachment/delete/<uuid:pk>/', lead_delete_attachment),


    # path('leads/by-source', leads_by_source),
    # path('leads/by-medium', leads_by_medium),
    # path('leads/by-stage', leads_by_stage),
    # path('leads/by-funnel-stage', funnel_stages),
    # path('leads/by-tag', leads_by_tag),
    # path('leads/by-branch', leads_by_branch),
    # path('leads/by-session', leads_by_session),
    # path('leads/monthly', monthly_leads),


    # path('lead/follow-ups/<uuid:pk>/', FollowUpView.as_view()),
    # path('lead/follow-ups', FollowUpView.as_view()),


    # path('lead/sources/<uuid:pk>/', SourceView.as_view()),
    # path('lead/sources', SourceView.as_view()),
    # path('lead/sources/status/update/<uuid:pk>/', change_source_status),


    # path('lead/stages/<uuid:pk>/', StageView.as_view()),
    # path('lead/stages', StageView.as_view()),
    # path('lead/stages/status/update/<uuid:pk>/', change_stage_status),
    # path('lead/stages/create/default', create_default_stages),


    # path('lead/tags/<uuid:pk>/', TagView.as_view()),
    # path('lead/tags', TagView.as_view()),
    # path('lead/tags/status/update/<uuid:pk>/', change_tag_status),

    # path('lead/trackings/<uuid:pk>/', TrackingView.as_view()),
    # path('lead/trackings', TrackingView.as_view()),

    # path('follow-up/types/<uuid:pk>/', FollowUpTypeView.as_view()),
    # path('follow-up/types', FollowUpTypeView.as_view()),
    # path('follow-up/types/status/update/<uuid:pk>/', change_follow_up_type_status),


]
