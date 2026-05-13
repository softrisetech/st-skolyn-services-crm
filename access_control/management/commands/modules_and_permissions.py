MODULES = [
    {"name": "Contacts", "is_active": True, "app_slug": "crm"},
    {"name": "Leads", "is_active": True, "app_slug": "crm"},
    {"name": "Reports", "is_active": True, "app_slug": "crm"},
    {"name": "Report Exports", "is_active": True, "app_slug": "crm"},
    {"name": "Teams", "is_active": True, "app_slug": "crm"},
    {"name": "Mediums", "is_active": True, "app_slug": "crm"},
    {"name": "Sources", "is_active": True, "app_slug": "crm"},
    {"name": "Campaigns", "is_active": True, "app_slug": "crm"},
    {"name": "Tags", "is_active": True, "app_slug": "crm"},
    {"name": "Stages", "is_active": True, "app_slug": "crm"},
    {"name": "Stage Reasons", "is_active": True, "app_slug": "crm"},
    {"name": "Follow Up Types", "is_active": True, "app_slug": "crm"},
    {"name": "Institutes", "is_active": True, "app_slug": "crm"},
    {"name": "Academic Year Targets", "is_active": True, "app_slug": "crm"},

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
                "frontend_url": "/crm/mediums/[:id]/edit",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/mediums/{id}/delete",
                "frontend_url": "/crm/mediums/[:id]/delete",
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
                "frontend_url": "/crm/sources/[:id]/edit",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/sources/{id}/delete",
                "frontend_url": "/crm/sources/[:id]/delete",
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
                "frontend_url": "/crm/stages/[:id]/edit",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/stages/{id}/delete",
                "frontend_url": "/crm/stages/[:id]/delete",
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
                "frontend_url": "/crm/tags/[:id]/edit",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/tags/{id}/delete",
                "frontend_url": "/crm/tags/[:id]/delete",
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
                "frontend_url": "/crm/stage-reasons/[:id]/edit",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/stages/reasons/{id}/delete",
                "frontend_url": "/crm/stage-reasons/[:id]/delete",
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
                "frontend_url": "/crm/campaigns/[:id]/edit",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/campaigns/{id}/delete",
                "frontend_url": "/crm/campaigns/[:id]/delete",
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
                "frontend_url": "/crm/follow-up-types/[:id]/edit",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/follow-up/types/{id}/delete",
                "frontend_url": "/crm/follow-up-types/[:id]/delete",
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
                "frontend_url": "/crm/teams/[:id]/edit",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/teams/{id}/delete",
                "frontend_url": "/crm/teams/[:id]/delete",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
            },
            {
                "name": "Branch Wise",
                "url": "",
                "frontend_url": "",
                "key": "team-branch-wise",
                "type": 2,
                "is_active": True,
                "sort_order": 5,
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
                "frontend_url": "/crm/contacts",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "Create",
                "url": "lead/contacts/store",
                "frontend_url": "/crm/contacts/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2,
            },
            {
                "name": "Edit",
                "url": "lead/contacts/{id}/update",
                "frontend_url": "/crm/contacts/[:id]/edit",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/contacts/{id}/delete",
                "frontend_url": "/crm/contacts/[:id]/delete",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
            },
            {
                "name": "Export",
                "url": "reports/export/contacts/",
                "frontend_url": "/crm/lead-contacts-exports",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 5
            },
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
                "key": "lead-read",
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
                "url": "leads/{id}/update, leads/{id}/change/stage, leads/quick/email",
                "frontend_url": "/crm/leads/[:id]/edit, /crm/leads/[:id]/follow-ups, /crm/leads/[:id]/trackings, /crm/leads/[:id]/pre-requisites",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "leads/{id}/delete, leads/{id}/attachment/<uuid:pk>/delete",
                "frontend_url": "/crm/leads/[:id]/delete",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4,
            },
            {
                "name": "Export",
                "url": "leads/export/",
                "frontend_url": "/crm/leads/export",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 5
            },
            {
                "name": "Branch Wise",
                "url": "",
                "frontend_url": "",
                "key": "branch-wise-leads",
                "type": 2,
                "is_active": True,
                "sort_order": 6,
            },
            {
                "name": "View All",
                "url": "",
                "frontend_url": "",
                "key": "lead-view-all",
                "type": 2,
                "is_active": True,
                "sort_order": 7,
            },
            {
                "name": "Modify All",
                "url": "",
                "frontend_url": "",
                "key": "lead-modify-all",
                "type": 2,
                "is_active": True,
                "sort_order": 8,
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
                "frontend_url": "/crm/institutes/[:id]/edit",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3,
            },
            {
                "name": "Delete",
                "url": "lead/institutes/{id}/delete",
                "frontend_url": "/crm/institutes/[:id]/delete",
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
                "name": "High Priority Pending Follow-Ups",
                "url": "reports/high-priority-no-followup",
                "frontend_url": "/crm/reports/high-priority",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1
            },
            {
                "name": "High Priority Exports",
                "url": "reports/export/high-priority-no-followup/",
                "frontend_url": "/crm/reports/high-priority-exports",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1
            },
            {
                "name": "Pending Follow-Ups",
                "url": "reports/no-followup-leads",
                "frontend_url": "/crm/reports/no-followup-leads",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2
            },
            {
                "name": "Pending Follow-Ups Export",
                "url": "reports/export/no-followup-leads/",
                "frontend_url": "/crm/reports/no-followup-leads-exports",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2
            },
            {
                "name": "Upcoming Follow-Ups",
                "url": "reports/upcoming-followups",
                "frontend_url": "/crm/reports/upcoming-followups",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3
            },
            {
                "name": "Upcoming Follow-Ups Export",
                "url": "reports/export/upcoming-followups/",
                "frontend_url": "/crm/reports/upcoming-followups-exports",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3
            },
            {
                "name": "Overdue Follow-Ups",
                "url": "reports/overdue-followups",
                "frontend_url": "/crm/reports/overdue-followups",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4
            },
            {
                "name": "Overdue Follow-Ups Export",
                "url": "reports/export/overdue-followups/",
                "frontend_url": "/crm/reports/overdue-followups-exports",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4
            },
            {
                "name": "Lost Leads Analysis",
                "url": "reports/lost-leads",
                "frontend_url": "/crm/reports/lost-leads",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 5
            },
            {
                "name": "Lost Leads Export",
                "url": "reports/export/lost-leads/",
                "frontend_url": "/crm/reports/lost-leads-exports",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 5
            },
        ]

    },
    {
        "module_name": "Academic Year Targets",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/session/targets/list, lead/session/targets/{id}/get",
                "frontend_url": "/crm/session-targets",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1
            },
            {
                "name": "Create",
                "url": "lead/session/targets/store",
                "frontend_url": "/crm/session-targets/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2
            },
            {
                "name": "Edit",
                "url": "lead/session/targets/{id}/update",
                "frontend_url": "/crm/session-targets/[:id]/edit",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3
            },
            {
                "name": "Delete",
                "url": "lead/session/targets/{id}/delete",
                "frontend_url": "/crm/session-targets/[:id]/delete",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4
            },
            {
                "name": "Branch Wise",
                "url": "",
                "frontend_url": "",
                "key": "session-target-branch-wise",
                "type": 2,
                "is_active": True,
                "sort_order": 5,
            }
        ]

    },
    {
        "module_name": "Academic Year Targets",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "lead/session/targets/list, lead/session/targets/{id}/get",
                "frontend_url": "/crm/session-targets",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1
            },
            {
                "name": "Create",
                "url": "lead/session/targets/store",
                "frontend_url": "/crm/session-targets/add",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 2
            },
            {
                "name": "Edit",
                "url": "lead/session/targets/{id}/update",
                "frontend_url": "/crm/session-targets/[:id]/edit",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 3
            },
            {
                "name": "Delete",
                "url": "lead/session/targets/{id}/delete",
                "frontend_url": "/crm/session-targets/[:id]/delete",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 4
            }
        ]

    },
    {
        "module_name": "Report Exports",
        "module_app_slug": "crm",
        "permissions": [
            {
                "name": "Read",
                "url": "report-exports/crm/, report-export/{id}/",
                "frontend_url": "/crm/report-exports",
                "key": "",
                "type": 1,
                "is_active": True,
                "sort_order": 1,
            },
            {
                "name": "View All",
                "url": "",
                "frontend_url": "",
                "key": "report-export-view-all",
                "type": 2,
                "is_active": True,
                "sort_order": 2,
            },
            
        ]

    },
]