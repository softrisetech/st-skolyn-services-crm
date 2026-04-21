from django.urls import path
from .views.rolePermissionViews import role_permissions, assign_permission_to_role
from .views.moduleViews import get_modules, store_module, update_module, delete_module, change_module_status
from .views.permissionViews import get_permissions, store_permission, update_permission, delete_permission, get_role_based_permissions, change_permission_status

urlpatterns = [

    path('modules/list/', get_modules),
    path('modules/retrieve/<uuid:pk>/', get_modules),
    path('modules/create/', store_module),
    path('modules/update/<uuid:pk>/', update_module),
    path('modules/delete/<uuid:pk>/', delete_module),
    path('modules/status/<uuid:pk>/', change_module_status),

    path('permissions/list/', get_permissions),
    path('permissions/retrieve/<uuid:pk>/', get_permissions),
    path('permissions/create/', store_permission),
    path('permissions/update/<uuid:pk>/', update_permission),
    path('permissions/delete/<uuid:pk>/', delete_permission),
    path('permissions/status/<uuid:pk>/', change_permission_status),
    path('permissions/role-based/', get_role_based_permissions),

    path('roles/<uuid:pk>/permissions/assign', assign_permission_to_role),
    path('roles/<uuid:pk>/permissions', role_permissions),
]