# -*- coding: utf-8 -*-
{
    'name': "Recurring Bill",

    'summary': """
        Recurring Bill""",

    'description': """
        Recurring Bill
    """,

    'author': "Viltco",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/server.xml',
        'views/recurring_bill_views.xml',
        'views/views.xml',
    ],

}
