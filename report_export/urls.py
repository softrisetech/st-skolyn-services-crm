from django.urls import path
from .views.reportExportViews import report_export_list, report_export_update

urlpatterns = [
    path('report-exports/crm/', report_export_list, name='report-export-list'),
    path('report-export/<uuid:pk>/', report_export_update, name='report-export-update'),
]