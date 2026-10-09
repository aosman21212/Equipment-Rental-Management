# -*- coding: utf-8 -*-
# =============================================================================
#  Equipment Rental Management
# -----------------------------------------------------------------------------
#  Location  : King Abdulaziz Branch Road, Riyadh, Saudi Arabia
#  Email     : sales@leapai.ai
#  Phone     : +966 53 553 3627
#  Website   : https://leapai.ai
#  Developer : Abdulkaraim Osman — Tech Manager | Backend Engineer | DevOps Engineer
#              at Bab International Corp For Specialized Services
#  LinkedIn  : https://www.linkedin.com/in/abdulkaraim-o-385b7a110/
# =============================================================================
{
    'name': 'Equipment Rental Management',
    'version': '19.0.1.0.0',
    'category': 'Operations/Rental',
    'summary': 'Complete Equipment Rental & Fleet Management Suite for Odoo 19',
    'description': """
Equipment Rental Management Suite
==================================
A production-quality equipment rental management solution including:
- Fleet registry with categories, status tracking, and rate management
- Quotation and contract management
- Dispatch and off-hire (return) management
- Operator management with competencies and licenses
- Compliance: inspections, certificates, audit trail
- Workshop jobs, breakdowns, preventive maintenance
- Usage logs, fuel logs, field expenses
- Profitability analysis per equipment and contract
- Full chatter/activity tracking on key documents
- QWeb PDF reports for quotations, contracts, and dispatch notes
    """,
    'author': 'leapai.ai',
    'maintainer': 'Abdulkaraim Osman',
    'support': 'sales@leapai.ai',
    'website': 'https://leapai.ai',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'account', 'stock', 'purchase', 'hr'],
    'application': True,
    'data': [
        'security/rental_security.xml',
        'security/ir.model.access.csv',
        'data/rental_sequence.xml',
        'views/rental_equipment_views.xml',
        'views/rental_quotation_views.xml',
        'views/rental_contract_views.xml',
        'views/rental_dispatch_views.xml',
        'views/rental_operator_views.xml',
        'views/rental_inspection_views.xml',
        'views/rental_workshop_views.xml',
        'views/rental_usage_views.xml',
        'views/rental_config_views.xml',
        'views/rental_menu.xml',
        'report/rental_quotation_report.xml',
        'report/rental_contract_report.xml',
        'report/rental_dispatch_report.xml',
    ],
    'demo': [
        'demo/rental_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'images': [
        'static/description/icon.png',
    ],
}
