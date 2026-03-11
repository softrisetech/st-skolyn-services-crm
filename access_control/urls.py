from django.urls import path
from .views.moduleViews import ModuleView, change_module_status
from .views.rolePermissionViews import role_permissions, assign_permission_to_role
from .views.permissionViews import *


urlpatterns = [
    path('roles/<uuid:pk>/permissions/assign', assign_permission_to_role),
    path('roles/<uuid:pk>/permissions', role_permissions),

    path('modules/<uuid:pk>/', ModuleView.as_view()),
    path('modules', ModuleView.as_view()),
    path('modules/status/update/<uuid:pk>/', change_module_status),

    path('permissions/list/', PermissionListAPIView.as_view()),
    path('permissions/retrieve/<uuid:pk>/', PermissionRetrieveAPIView.as_view()),
    path('permissions/create/', PermissionCreateAPIView.as_view()),
    path('permissions/update/<uuid:pk>/', PermissionUpdateAPIView.as_view()),
    path('permissions/delete/<uuid:pk>/', PermissionDeleteAPIView.as_view()),
    path('permissions/status/<uuid:pk>/', change_permission_status),

    path('permissions/role-based/', get_role_based_permissions),
]
