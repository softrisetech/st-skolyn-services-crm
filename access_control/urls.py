from django.urls import path
from .views.moduleViews import ModuleView, change_module_status
from .views.rolePermissionViews import role_permissions, assign_permission_to_role
from .views.permissionViews import PermissionView, get_role_based_permissions, change_permission_status

urlpatterns = [
    path('roles/<uuid:pk>/permissions/assign', assign_permission_to_role),
    path('roles/<uuid:pk>/permissions', role_permissions),

    path('modules/<uuid:pk>/', ModuleView.as_view()),
    path('modules', ModuleView.as_view()),
    path('modules/status/update/<uuid:pk>/', change_module_status),

    path('permissions/<uuid:pk>/', PermissionView.as_view()),
    path('permissions', PermissionView.as_view()),
    path('permissions/role-based', get_role_based_permissions),
    path('permissions/status/update/<uuid:pk>/', change_permission_status),
]
