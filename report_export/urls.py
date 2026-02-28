from django.urls import path
from .views.reportExportViews import ReportExportListAPIView, ReportExportUpdateAPIView

urlpatterns = [
    path('report-exports/list/', ReportExportListAPIView.as_view(), name='report-export-list'),
    path('report-exports/update/<uuid:pk>/', ReportExportUpdateAPIView.as_view(), name='report-export-update'),
]