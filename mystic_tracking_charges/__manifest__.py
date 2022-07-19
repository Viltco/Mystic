# -*- coding: utf-8 -*-
{
    'name': "Mystic Tracking Charges",

    'summary': """
        Mystic Tracking Charges""",

    'description': """
        This Module deals with tracking charges
    """,

    'author': "Viltco",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'fleet',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fleet', 'branch', 'mystic_insurance'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/server.xml',
        'views/tracking_charges_views.xml',
        'views/tracking_line_tree_views.xml',
        'wizards/tracking_charges_wizard.xml',
    ],

}
