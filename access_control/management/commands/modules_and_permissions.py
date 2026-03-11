MODULES = [
    {"name": "Mediums", "is_active": True, "app_slug": "crm"},
    {"name": "Sources", "is_active": True, "app_slug": "crm"},
    {"name": "Stages", "is_active": True, "app_slug": "crm"},
    {"name": "Tags", "is_active": True, "app_slug": "crm"},
    {"name": "Stage Reasons", "is_active": True, "app_slug": "crm"},
    {"name": "Campaigns", "is_active": True, "app_slug": "crm"},
    {"name": "Follow Up Types", "is_active": True, "app_slug": "crm"},
    {"name": "Teams", "is_active": True, "app_slug": "crm"},
    {"name": "Contacts", "is_active": True, "app_slug": "crm"},
    {"name": "Leads", "is_active": True, "app_slug": "crm"},
    {"name": "Follow Ups", "is_active": True, "app_slug": "crm"},
    {"name": "Institutes", "is_active": True, "app_slug": "crm"},
]


PERMISSIONS = [
    {
        "module_name": "Mediums",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/mediums/list, lead/mediums/{id}/get",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Create",
                "url": "lead/mediums/store",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Edit",
                "url": "lead/mediums/{id}/update",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Delete",
                "url": "lead/mediums/{id}/delete",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            }
        ]

    },
    {
        "module_name": "Sources",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/sources/list, lead/sources/{id}/get",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Create",
                "url": "lead/sources/store",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Edit",
                "url": "lead/sources/{id}/update",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Delete",
                "url": "lead/sources/{id}/delete",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            }
        ]

    },
    {
        "module_name": "Stages",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/stages/list, lead/stages/{id}/get",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Create",
                "url": "lead/stages/store",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Edit",
                "url": "lead/stages/{id}/update",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Delete",
                "url": "lead/stages/{id}/delete",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            }
        ]

    },
    {
        "module_name": "Tags",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/tags/list, lead/tags/{id}/get",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Create",
                "url": "lead/tags/store",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Edit",
                "url": "lead/tags/{id}/update",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Delete",
                "url": "lead/tags/{id}/delete",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            }
        ]

    },
    {
        "module_name": "Stage Reasons",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/stages/reasons/list, lead/stages/reasons/{id}/get",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Create",
                "url": "lead/stages/reasons/store",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Edit",
                "url": "lead/stages/reasons/{id}/update",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Delete",
                "url": "lead/stages/reasons/{id}/delete",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            }
        ]

    },
    {
        "module_name": "Campaigns",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/campaigns/list, lead/campaigns/{id}/get",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Create",
                "url": "lead/campaigns/store",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Edit",
                "url": "lead/campaigns/{id}/update",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Delete",
                "url": "lead/campaigns/{id}/delete",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            }
        ]

    },
    {
        "module_name": "Follow Up Types",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/follow-up/types/list, lead/follow-up/types/{id}/get",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Create",
                "url": "lead/follow-up/types/store",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Edit",
                "url": "lead/follow-up/types/{id}/update",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Delete",
                "url": "lead/follow-up/types/{id}/delete",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            }
        ]

    },
    {
        "module_name": "Teams",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/teams/list, lead/teams/{id}/get",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Create",
                "url": "lead/teams/store",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Edit",
                "url": "lead/teams/{id}/update",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Delete",
                "url": "lead/teams/{id}/delete",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            }
        ]

    },
    {
        "module_name": "Contacts",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/contacts/list, lead/contacts/{id}/get",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Create",
                "url": "lead/contacts/store",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Edit",
                "url": "lead/contacts/{id}/update",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Delete",
                "url": "lead/contacts/{id}/delete",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            }
        ]

    },
    {
        "module_name": "Leads",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "leads/list, leads/{id}/get",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Create",
                "url": "leads/store",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Edit",
                "url": "leads/{id}/update, leads/{id}/change/stage",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "Delete",
                "url": "leads/{id}/delete, leads/{id}/attachment/<uuid:pk>/delete",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
            },
            {
                "name": "View All",
                "url": "",
                "frontend_url": "",
                "key": "lead-view-all",
                "type": 2,
                "is_active": True,
            },
            {
                "name": "Modify All",
                "url": "",
                "frontend_url": "",
                "key": "lead-modify-all",
                "type": 2,
                "is_active": True,
            },
            {
                "name": "Branch Wise",
                "url": "",
                "frontend_url": "",
                "key": "branch-wise-leads",
                "type": 2,
                "is_active": True,
            }
        ]

    }
]