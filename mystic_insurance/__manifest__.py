# -*- coding: utf-8 -*-
{
    'name': "Mystic Insurance",

    'summary': """
        Mystic Insurance""",

    'description': """
        This Module deals with fleet insurance
    """,

    'author': "Viltco",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'fleet',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fleet', 'branch'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/server.xml',
        'views/insurance_line_tree_views.xml',
        'views/insurance_views.xml',
        'wizards/insurance_wizard.xml',
    ],

}
