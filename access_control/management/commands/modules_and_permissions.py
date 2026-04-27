MODULES = [
    {"name": "Mediums", "is_active": True, "app_slug": "crm", "sort_order": 1},
    {"name": "Sources", "is_active": True, "app_slug": "crm", "sort_order": 2},
    {"name": "Stages", "is_active": True, "app_slug": "crm", "sort_order": 3},
    {"name": "Tags", "is_active": True, "app_slug": "crm", "sort_order": 4},
    {"name": "Stage Reasons", "is_active": True, "app_slug": "crm", "sort_order": 5},
    {"name": "Campaigns", "is_active": True, "app_slug": "crm", "sort_order": 6},
    {"name": "Follow Up Types", "is_active": True, "app_slug": "crm", "sort_order": 7},
    {"name": "Teams", "is_active": True, "app_slug": "crm", "sort_order": 8},
    {"name": "Contacts", "is_active": True, "app_slug": "crm", "sort_order": 9},
    {"name": "Leads", "is_active": True, "app_slug": "crm", "sort_order": 10},
    {"name": "Institutes", "is_active": True, "app_slug": "crm", "sort_order": 11},
    {"name": "Reports", "is_active": True, "app_slug": "crm", "sort_order": 12},
]


PERMISSIONS = [
    {
        "module_name": "Mediums",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/mediums/list, lead/mediums/{id}/get",
                "frontend_url": "/crm/mediums",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "Create",
                "url": "lead/mediums/store",
                "frontend_url": "/crm/mediums/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2,
            },
            {
                "name": "Edit",
                "url": "lead/mediums/{id}/update",
                "frontend_url": "/crm/mediums/edit/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/mediums/{id}/delete",
                "frontend_url": "/crm/mediums/delete/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
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
                "frontend_url": "/crm/sources",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "Create",
                "url": "lead/sources/store",
                "frontend_url": "/crm/sources/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2,
            },
            {
                "name": "Edit",
                "url": "lead/sources/{id}/update",
                "frontend_url": "/crm/sources/edit/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/sources/{id}/delete",
                "frontend_url": "/crm/sources/delete/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
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
                "frontend_url": "/crm/stages",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "Create",
                "url": "lead/stages/store",
                "frontend_url": "/crm/stages/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2,
            },
            {
                "name": "Edit",
                "url": "lead/stages/{id}/update",
                "frontend_url": "/crm/stages/edit/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/stages/{id}/delete",
                "frontend_url": "/crm/stages/delete/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
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
                "frontend_url": "/crm/tags",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "Create",
                "url": "lead/tags/store",
                "frontend_url": "/crm/tags/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2,
            },
            {
                "name": "Edit",
                "url": "lead/tags/{id}/update",
                "frontend_url": "/crm/tags/edit/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/tags/{id}/delete",
                "frontend_url": "/crm/tags/delete/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
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
                "frontend_url": "/crm/stage-reasons",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "Create",
                "url": "lead/stages/reasons/store",
                "frontend_url": "/crm/stage-reasons/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2,
            },
            {
                "name": "Edit",
                "url": "lead/stages/reasons/{id}/update",
                "frontend_url": "/crm/stage-reasons/edit/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/stages/reasons/{id}/delete",
                "frontend_url": "/crm/stage-reasons/delete/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
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
                "frontend_url": "/crm/campaigns",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "Create",
                "url": "lead/campaigns/store",
                "frontend_url": "/crm/campaigns/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2,
            },
            {
                "name": "Edit",
                "url": "lead/campaigns/{id}/update",
                "frontend_url": "/crm/campaigns/edit/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/campaigns/{id}/delete",
                "frontend_url": "/crm/campaigns/delete/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
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
                "frontend_url": "/crm/follow-up-types",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "Create",
                "url": "lead/follow-up/types/store",
                "frontend_url": "/crm/follow-up-types/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2,
            },
            {
                "name": "Edit",
                "url": "lead/follow-up/types/{id}/update",
                "frontend_url": "/crm/follow-up-types/edit/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/follow-up/types/{id}/delete",
                "frontend_url": "/crm/follow-up-types/delete/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
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
                "frontend_url": "/crm/teams",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "Create",
                "url": "lead/teams/store",
                "frontend_url": "/crm/teams/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2,
            },
            {
                "name": "Edit",
                "url": "lead/teams/{id}/update",
                "frontend_url": "/crm/teams/edit/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/teams/{id}/delete",
                "frontend_url": "/crm/teams/delete/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
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
                "sort_order": 1,
            },
            {
                "name": "Create",
                "url": "lead/contacts/store",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2,
            },
            {
                "name": "Edit",
                "url": "lead/contacts/{id}/update",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/contacts/{id}/delete",
                "frontend_url": "",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
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
                "frontend_url": "/crm/leads",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "Create",
                "url": "leads/store",
                "frontend_url": "/crm/leads/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2,
            },
            {
                "name": "Edit",
                "url": "leads/{id}/update, leads/{id}/change/stage",
                "frontend_url": "/crm/leads/edit/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "leads/{id}/delete, leads/{id}/attachment/<uuid:pk>/delete",
                "frontend_url": "/crm/leads/delete/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
            },
            {
                "name": "Branch Wise",
                "url": "",
                "frontend_url": "",
                "key": "branch-wise-leads",
                "type": 2,
                "is_active": True,
                "sort_order": 5,
            },
            {
                "name": "View All",
                "url": "",
                "frontend_url": "",
                "key": "lead-view-all",
                "type": 2,
                "is_active": True,
                "sort_order": 6,
            },
            {
                "name": "Modify All",
                "url": "",
                "frontend_url": "",
                "key": "lead-modify-all",
                "type": 2,
                "is_active": True,
                "sort_order": 7,
            },
        ]

    },
    {
        "module_name": "Institutes",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/institutes/list, lead/institutes/{id}/get",
                "frontend_url": "/crm/institutes",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "Create",
                "url": "lead/institutes/store",
                "frontend_url": "/crm/institutes/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2,
            },
            {
                "name": "Edit",
                "url": "lead/institutes/{id}/update",
                "frontend_url": "/crm/institutes/edit/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/institutes/{id}/delete",
                "frontend_url": "/crm/institutes/delete/[id]",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
            }
        ]

    },
    {
        "module_name": "Reports",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "No Follow Up Leads (High Priority)",
                "url": "reports/high-priority-no-followup",
                "frontend_url": "/crm/reports/high-priority",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1
            },
            {
                "name": "No Follow Up Leads",
                "url": "reports/no-followup-leads",
                "frontend_url": "/crm/reports/no-followup-leads",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2
            },
            {
                "name": "Upcoming Follow Ups",
                "url": "reports/upcoming-followups",
                "frontend_url": "/crm/reports/upcoming-followups",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3
            },
            {
                "name": "Overdue Follow Ups",
                "url": "reports/overdue-followups",
                "frontend_url": "/crm/reports/overdue-followups",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4
            },
            {
                "name": "Lost Leads",
                "url": "reports/lost-leads",
                "frontend_url": "/crm/reports/lost-leads",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 5
            },
        ]

    },
]