# -*- coding: utf-8 -*-
{
    'name': "non_revenue_ticket",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base' , 'fleet'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'report/report.xml',
        'report/report1.xml',
        'views/non_revenue_ticket.xml',
        'wizard/move_wizard.xml',
        'wizard/return_wizard.xml',
        'wizard/nrt_report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
