# -*- coding: utf-8 -*-
{
    'name': "branch_accounting",

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
    'depends': ['base','branch','branch_customization','account', 'AG_multiinvoice_payment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_payment_inherited.xml',
        'views/branch_inherited_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
