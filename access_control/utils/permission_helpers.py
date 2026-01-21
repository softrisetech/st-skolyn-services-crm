from ..models import Permission, RolePermission

def view_modify_all(user_id, role_id, key):
    permission = Permission.objects.filter(key=key).first()
    if not permission:
        return False

    role_permissions = RolePermission.objects.filter(role_id=role_id, permission=permission)
    if not role_permissions:
        return False

    return True

def view_branch_wise(user_id, role_id, key):
    permission = Permission.objects.filter(key=key).first()
    if not permission:
        return False

    role_permissions = RolePermission.objects.filter(role_id=role_id, permission=permission)
    if not role_permissions:
        return False

    return True