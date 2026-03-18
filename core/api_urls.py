from django.urls import path
from core.views.auditLog import get_activity_logs

urlpatterns = [
    path('audit-logs/list/', get_activity_logs, name='audit-log-list'),
]