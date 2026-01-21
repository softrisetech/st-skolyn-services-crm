from django.urls import path
from .views.permissionViews import *
from .views.moduleViews import ModuleView, change_module_status
from .views.rolePermissionViews import role_permissions, assign_permission_to_role

urlpatterns = [
    path('roles/<uuid:pk>/permissions/assign', assign_permission_to_role, name='role-permissions-assign'),
    path('roles/<uuid:pk>/permissions', role_permissions, name='role-permissions'),

    path('modules/<uuid:pk>/', ModuleView.as_view(), name='module-detail'),
    path('modules', ModuleView.as_view(), name='modules'),
    path('modules/status/update/<uuid:pk>/', change_module_status, name='module-status-update'),

    path('permissions/<uuid:pk>/', PermissionView.as_view(), name='permission-detail'),
    path('permissions', PermissionView.as_view(), name='permissions'),
    path('permissions/role-based', get_role_based_permissions),
    path('permissions/status/update/<uuid:pk>/', change_permission_status, name='permission-status-update'),
]
