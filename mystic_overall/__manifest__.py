# -*- coding: utf-8 -*-
{
    'name': "mystic_overall",

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
    'depends': ['base' , 'fleet' , 'account' , 'branch','product','purchase' ,'vehicle_reservation' , 'sale','stock' ,'account_asset'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/fleet_customization.xml',
        'views/branch_inherit.xml',
        'views/product_inherit.xml',
        'views/purchase_inherit.xml',
        'views/account_inherit.xml',
        'views/sale_inherit.xml',
        # 'views/requisition_branch_seq.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
