# -*- coding: utf-8 -*-
{
    'name': "Lease Bill",

    'summary': """
        Lease Bill Customization""",

    'description': """
        Lease Bill Customization
    """,

    'author': "Viltco",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','advance_payment_purchase', 'branch'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'wizards/lease_wizard.xml',
        'wizards/lease_payment_wizard.xml',
        'views/account_move_views.xml',
        'views/lease_bill_views.xml',
        'views/lease_bill_lines_view.xml',
    ],

}
