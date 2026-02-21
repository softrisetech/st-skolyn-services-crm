from django.db import connection
from django.core.management.base import BaseCommand
from ...models import Module, Permission
import json

class Command(BaseCommand):
    help = 'Seed the database with module data'

    def handle(self, *args, **kwargs):
        # app_id = "a1aee7bd-711a-4c6c-87b0-f5f4386aed4b"
        # modules = [
        #     {
        #         "app_id": app_id,
        #         "name": "Leads",
        #         "is_active": True,
        #         "app_slug": "crm",
        #         "sort_order": 1
        #     },{
        #         "app_id": app_id,
        #         "name": "Mediums",
        #         "is_active": True,
        #         "app_slug": "crm",
        #         "sort_order": 2
        #     },{
        #         "app_id": app_id,
        #         "name": "Sources",
        #         "is_active": True,
        #         "app_slug": "crm",
        #         "sort_order": 3
        #     },{
        #         "app_id": app_id,
        #         "name": "Tags",
        #         "is_active": True,
        #         "app_slug": "crm",
        #         "sort_order": 4
        #     },{
        #         "app_id": app_id,
        #         "name": "Stages",
        #         "is_active": True,
        #         "app_slug": "crm",
        #         "sort_order": 5
        #     },{
        #         "app_id": app_id,
        #         "name": "Follow Up Types",
        #         "is_active": True,
        #         "app_slug": "crm",
        #         "sort_order": 6
        #     },
        #     {
        #         "app_id": app_id,
        #         "name": "Lost Reasons",
        #         "is_active": True,
        #         "app_slug": "crm",
        #         "sort_order": 7
        #     }
        # ]

        # for module_data in modules:
        #     module = Module.objects.filter(name=module_data["name"]).first()

        #     if module:
        #         updated = False

        #         # Update only `is_active`
        #         if module.is_active != module_data["is_active"]:
        #             module.is_active = module_data["is_active"]
        #             updated = True

        #         # Update `app_slug` if changed
        #         if module.app_slug != module_data.get("app_slug"):
        #             module.app_slug = module_data.get("app_slug")
        #             updated = True

        #         if updated:
        #             module.save()
        #             self.stdout.write(self.style.WARNING(f'Module updated: {module.name}'))
        #         else:
        #             self.stdout.write(self.style.NOTICE(f'Module already up-to-date: {module.name}'))

        #     else:
        #         # Create a new module including app_id
        #         module = Module.objects.create(
        #             name=module_data["name"],
        #             app_id=module_data["app_id"],
        #             is_active=module_data["is_active"],
        #             app_slug=module_data["app_slug"],
        #             sort_order=module_data["sort_order"]
        #         )
        #         self.stdout.write(self.style.SUCCESS(f'Module created: {module.name}'))

        # self.stdout.write(self.style.SUCCESS('Module seeding completed successfully!'))

        # permissions = []
        # modules = Module.objects.all()
        # for module in modules:
        #     if module.name == "Tags":
        #         permissions.extend([
        #             {
        #                 "name": "Read",
        #                 "url": "lead/tags, lead/tags/{id}",
        #                 "frontend_url": "/crm/configurations/tags",
        #                 "request_method": "GET",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 1,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Create",
        #                 "url": "lead/tags",
        #                 "frontend_url": "/crm/configurations/tags/create",
        #                 "request_method": "POST",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 2,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Edit",
        #                 "url": "lead/tags/{id}, lead/tags/status/update/{id}",
        #                 "frontend_url": "/crm/configurations/tags/:id/edit",
        #                 "request_method": "PUT, PATCH",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 3,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Delete",
        #                 "url": "lead/tags/{id}",
        #                 "frontend_url": "/crm/configurations/tags/:id/delete",
        #                 "request_method": "DELETE",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 4,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             }
        #         ])

        #     if module.name == "Mediums":
        #         permissions.extend([
        #             {
        #                 "name": "Read",
        #                 "url": "lead/mediums, lead/mediums/{id}",
        #                 "frontend_url": "/crm/configurations/medium",
        #                 "request_method": "GET",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 1,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Create",
        #                 "url": "lead/mediums",
        #                 "frontend_url": "/crm/configurations/medium/create",
        #                 "request_method": "POST",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 2,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Edit",
        #                 "url": "lead/mediums/{id}, lead/mediums/status/update/{id}",
        #                 "frontend_url": "/crm/configurations/medium/:id/edit",
        #                 "request_method": "PUT, PATCH",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 3,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Delete",
        #                 "url": "lead/mediums/{id}",
        #                 "frontend_url": "/crm/configurations/medium/:id/delete",
        #                 "request_method": "DELETE",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 4,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             }
        #         ])

        #     if module.name == "Sources":
        #         permissions.extend([
        #             {
        #                 "name": "Read",
        #                 "url": "lead/sources, lead/sources/{id}",
        #                 "frontend_url": "/crm/configurations/source",
        #                 "request_method": "GET",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 1,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Create",
        #                 "url": "lead/sources",
        #                 "frontend_url": "/crm/configurations/source/create",
        #                 "request_method": "POST",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 2,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Edit",
        #                 "url": "lead/sources/{id}, lead/sources/status/update/{id}",
        #                 "frontend_url": "/crm/configurations/source/:id/edit",
        #                 "request_method": "PUT, PATCH",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 3,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Delete",
        #                 "url": "lead/sources/{id}",
        #                 "frontend_url": "/crm/configurations/source/:id/delete",
        #                 "request_method": "DELETE",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 4,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             }
        #         ])

        #     if module.name == "Stages":
        #         permissions.extend([
        #             {
        #                 "name": "Read",
        #                 "url": "lead/stages, lead/stages/{id}",
        #                 "frontend_url": "/crm/configurations/lead/stage,/crm/configurations/opportunity/stage",
        #                 "request_method": "GET",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 1,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Create",
        #                 "url": "lead/stages",
        #                 "frontend_url": "/crm/configurations/lead/stage/create,/crm/configurations/opportunity/stage/create",
        #                 "request_method": "POST",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 2,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Edit",
        #                 "url": "lead/stages/{id}, lead/stages/status/update/{id}",
        #                 "frontend_url": "/crm/configurations/lead/stage/:id/edit,/crm/configurations/opportunity/stage/:id/edit",
        #                 "request_method": "PUT, PATCH",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 3,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Delete",
        #                 "url": "lead/stages/{id}",
        #                 "frontend_url": "/crm/configurations/lead/stage/:id/delete,/crm/configurations/opportunity/stage/:id/delete",
        #                 "request_method": "DELETE",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 4,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             }
        #         ])

        #     if module.name == "Leads":
        #         permissions.extend([
        #             {
        #                 "name": "Read",
        #                 "url": "leads, leads/{id}, lead/trackings, lead/trackings/{id}, lead/follow-ups, lead/follow-ups/{id}",
        #                 "frontend_url": "/crm/lead",
        #                 "request_method": "GET",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 1,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Create",
        #                 "url": "leads/create",
        #                 "frontend_url": "/crm/lead/create",
        #                 "request_method": "POST",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 2,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Edit",
        #                 "url": "leads/update/{id}, leads/change/stage/{id}",
        #                 "frontend_url": "/crm/lead/:id/edit,/crm/lead/create-follow-up,/crm/lead/:id/follow-up, leads/attachment/delete/{id}",
        #                 "request_method": "PUT, PATCH, DELETE",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 3,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Delete",
        #                 "url": "leads/delete/{id}",
        #                 "frontend_url": "/crm/lead/:id/delete",
        #                 "request_method": "DELETE",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 4,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "View All",
        #                 "url": "",
        #                 "frontend_url": "",
        #                 "request_method": "GET",
        #                 "key": "lead-view-all",
        #                 "type": 2,
        #                 "sort_order": 5,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Modify All",
        #                 "url": "",
        #                 "frontend_url": "",
        #                 "request_method": "PUT",
        #                 "key": "lead-modify-all",
        #                 "type": 2,
        #                 "sort_order": 6,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #              {
        #                  "name": "Branch Wise",
        #                  "url": "",
        #                  "frontend_url": "",
        #                  "request_method": "GET",
        #                  "key": "branch-wise-leads",
        #                  "type": 2,
        #                  "sort_order": 7,
        #                  "is_active": True,
        #                  "module_id": module.id
        #              },{
        #                    "name": "Import",
        #                    "url": "leads/import",
        #                    "frontend_url": "/crm/lead/import",
        #                    "request_method": "POST",
        #                    "key": "",
        #                    "type": 1,
        #                    "sort_order": 8,
        #                    "is_active": True,
        #                    "module_id": module.id
        #               },{
        #                    "name": "Export",
        #                    "url": "leads/export",
        #                    "frontend_url": "/crm/lead/export",
        #                    "request_method": "POST",
        #                    "key": "",
        #                    "type": 1,
        #                    "sort_order": 9,
        #                    "is_active": True,
        #                    "module_id": module.id
        #                }
        #         ])

        #     if module.name == "Follow Up Types":
        #         permissions.extend([
        #             {
        #                 "name": "Read",
        #                 "url": "follow-up/types, follow-up/types/{id}",
        #                 "frontend_url": "/crm/configurations/follow-up/types",
        #                 "request_method": "GET",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 1,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Create",
        #                 "url": "follow-up/types",
        #                 "frontend_url": "/crm/configurations/follow-up/types/create",
        #                 "request_method": "POST",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 2,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Edit",
        #                 "url": "follow-up/types/{id}, follow-up/types/status/update/{id}",
        #                 "frontend_url": "/crm/configurations/follow-up/types/:id/edit",
        #                 "request_method": "PUT, PATCH",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 3,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #              {
        #                  "name": "Delete",
        #                  "url": "follow-up/types/{id}",
        #                  "frontend_url": "/crm/configurations/follow-up/types/:id/delete",
        #                  "request_method": "DELETE",
        #                  "key": "",
        #                  "type": 1,
        #                  "sort_order": 4,
        #                  "is_active": True,
        #                  "module_id": module.id
        #              }
        #         ])

        #     if module.name == "Lost Reasons":
        #         permissions.extend([
        #             {
        #                 "name": "Read",
        #                 "url": "lead/lost/reasons, lead/lost/reasons/{id}",
        #                 "frontend_url": "/crm/configurations/lost-reasons",
        #                 "request_method": "GET",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 1,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Create",
        #                 "url": "lead/lost/reasons",
        #                 "frontend_url": "/crm/configurations/lost-reasons/create",
        #                 "request_method": "POST",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 2,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #             {
        #                 "name": "Edit",
        #                 "url": "lead/lost/reasons/{id}, lead/lost/reasons/status/update/{id}",
        #                 "frontend_url": "/crm/configurations/lost-reasons/:id/edit",
        #                 "request_method": "PUT, PATCH",
        #                 "key": "",
        #                 "type": 1,
        #                 "sort_order": 3,
        #                 "is_active": True,
        #                 "module_id": module.id
        #             },
        #              {
        #                  "name": "Delete",
        #                  "url": "lead/lost/reasons/{id}",
        #                  "frontend_url": "/crm/configurations/lost-reasons/:id/delete",
        #                  "request_method": "DELETE",
        #                  "key": "",
        #                  "type": 1,
        #                  "sort_order": 4,
        #                  "is_active": True,
        #                  "module_id": module.id
        #              }
        #         ])

        # # Ensure there are permissions to seed before proceeding
        # if not permissions:
        #     self.stdout.write(self.style.WARNING('No permissions to seed!'))
        #     return

        # for permission_data in permissions:
        #     permission, created = Permission.objects.update_or_create(
        #         name=permission_data["name"],
        #         module_id=permission_data["module_id"],
        #         defaults={
        #             "request_method": permission_data["request_method"],
        #             "url": permission_data["url"],
        #             "frontend_url": permission_data["frontend_url"],
        #             "key": permission_data["key"],
        #             "name": permission_data["name"],
        #             "type": permission_data["type"],
        #             "sort_order": permission_data["sort_order"],
        #             "is_active": permission_data["is_active"]
        #         }
        #     )
        #     if created:
        #         self.stdout.write(self.style.SUCCESS(f'Permission created: {permission.name}'))
        #     else:
        #         self.stdout.write(self.style.SUCCESS(f'Permission updated: {permission.name}'))

        self.stdout.write(self.style.SUCCESS('Permission seeding completed successfully!'))
