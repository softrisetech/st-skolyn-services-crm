from django.urls import path
from .views.followUpViews import FollowUpView
from .views.trackingViews import TrackingView
from .views.tagViews import TagView, change_tag_status
from .views.mediumViews import MediumView, change_medium_status
from .views.sourceViews import SourceView, change_source_status
from .views.followUpTypeViews import FollowUpTypeView, change_follow_up_type_status
from .views.stageViews import StageView, change_stage_status, create_default_stages
from .views.lostReasonViews import LostReasonView, change_lost_reason_status
from .views.dashboardViews import leads_by_source, leads_by_medium, leads_by_stage, funnel_stages, leads_by_tag, leads_by_branch, leads_by_session, monthly_leads
from .views.leadViews import lead_list, lead_list_stage_wise, import_leads, export_leads, lead_create, lead_update, lead_delete, lead_change_stage, lead_delete_attachment

urlpatterns = [
    path('leads/', lead_list),
    path('leads/stage-wise/', lead_list_stage_wise),
    path('leads/stage-wise/<uuid:pk>/', lead_list_stage_wise),
    path('leads/import/', import_leads),
    path('leads/export/', export_leads),
    path('leads/<uuid:pk>/', lead_list),
    path('leads/create/', lead_create),
    path('leads/update/<uuid:pk>/', lead_update),
    path('leads/delete/<uuid:pk>/', lead_delete),
    path('leads/change/stage/<uuid:pk>/', lead_change_stage),
    path('leads/attachment/delete/<uuid:pk>/', lead_delete_attachment),


    path('leads/by-source', leads_by_source),
    path('leads/by-medium', leads_by_medium),
    path('leads/by-stage', leads_by_stage),
    path('leads/by-funnel-stage', funnel_stages),
    path('leads/by-tag', leads_by_tag),
    path('leads/by-branch', leads_by_branch),
    path('leads/by-session', leads_by_session),
    path('leads/monthly', monthly_leads),


    path('lead/follow-ups/<uuid:pk>/', FollowUpView.as_view()),
    path('lead/follow-ups', FollowUpView.as_view()),

    path('lead/mediums/<uuid:pk>/', MediumView.as_view()),
    path('lead/mediums', MediumView.as_view()),
    path('lead/mediums/status/update/<uuid:pk>/', change_medium_status),

    path('lead/sources/<uuid:pk>/', SourceView.as_view()),
    path('lead/sources', SourceView.as_view()),
    path('lead/sources/status/update/<uuid:pk>/', change_source_status),


    path('lead/stages/<uuid:pk>/', StageView.as_view()),
    path('lead/stages', StageView.as_view()),
    path('lead/stages/status/update/<uuid:pk>/', change_stage_status),
    path('lead/stages/create/default', create_default_stages),


    path('lead/tags/<uuid:pk>/', TagView.as_view()),
    path('lead/tags', TagView.as_view()),
    path('lead/tags/status/update/<uuid:pk>/', change_tag_status),

    path('lead/trackings/<uuid:pk>/', TrackingView.as_view()),
    path('lead/trackings', TrackingView.as_view()),

    path('follow-up/types/<uuid:pk>/', FollowUpTypeView.as_view()),
    path('follow-up/types', FollowUpTypeView.as_view()),
    path('follow-up/types/status/update/<uuid:pk>/', change_follow_up_type_status),

    path('lead/lost/reasons/<uuid:pk>/', LostReasonView.as_view()),
    path('lead/lost/reasons', LostReasonView.as_view()),
    path('lead/lost/reasons/status/update/<uuid:pk>/', change_lost_reason_status),

]
