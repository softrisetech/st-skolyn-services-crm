from django.db import connection
from django.core.management.base import BaseCommand
from ...models import Module, Permission
from access_control.management.commands.modules_and_permissions import MODULES, PERMISSIONS


def normalize(value):
    return value.strip().lower()

class Command(BaseCommand):
    help = 'Seed the database with module data'

    def handle(self, *args, **kwargs):
        modules = MODULES

        for index, module_data in enumerate(modules, start=1):
            module = Module.objects.filter(name=module_data["name"]).first()

            if module:
                updated = False

                # Update only `is_active`
                if module.is_active != module_data["is_active"]:
                    module.is_active = module_data["is_active"]
                    updated = True

                # Update `app_slug` if changed
                if module.app_slug != module_data.get("app_slug"):
                    module.app_slug = module_data.get("app_slug")
                    updated = True

                if module.sort_order != index:
                    module.sort_order = index
                    updated = True

                if updated:
                    module.save()
                    self.stdout.write(self.style.WARNING(f'Module updated: {module.name}'))
                else:
                    self.stdout.write(self.style.NOTICE(f'Module already up-to-date: {module.name}'))

            else:
                # Create a new module including app_id
                module = Module.objects.create(
                    name=module_data["name"],
                    is_active=module_data["is_active"],
                    app_slug=module_data["app_slug"],
                    sort_order=index
                )
                self.stdout.write(self.style.SUCCESS(f'Module created: {module.name}'))

        self.stdout.write(self.style.SUCCESS('Module seeding completed successfully!'))

        permissions = []
        modules = Module.objects.all()

        permission_map = {
            (normalize(p["module_name"]), normalize(p["module_app_slug"])): p["permissions"]
            for p in PERMISSIONS
        }

        for module in modules:
            key = (normalize(module.name), normalize(module.app_slug))

            if key in permission_map:
                for index, perm in enumerate(permission_map[key], start=1):
                    permissions.append({
                        **perm,
                        "module_id": module.id,
                        "sort_order": index
                    })
                
        # Ensure there are permissions to seed before proceeding
        if not permissions:
            self.stdout.write(self.style.WARNING('No permissions to seed!'))
            return

        for permission_data in permissions:
            permission, created = Permission.objects.update_or_create(
                name=permission_data["name"],
                module_id=permission_data["module_id"],
                defaults={
                    "url": permission_data["url"],
                    "frontend_url": permission_data["frontend_url"],
                    "key": permission_data["key"],
                    "name": permission_data["name"],
                    "type": permission_data["type"],
                    "sort_order": permission_data["sort_order"],
                    "is_active": permission_data["is_active"]
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Permission created: {permission.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Permission updated: {permission.name}'))

        self.stdout.write(self.style.SUCCESS('Permission seeding completed successfully!'))