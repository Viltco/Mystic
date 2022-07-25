# -*- coding: utf-8 -*-
{
    'name': "Shift Addition Attendance",

    'summary': """
        Shift Addition Attendance By Dynexcel""",

    'description': """
        This Module works with attendance shift management
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.co",
    'category': 'Attendance',
    'version': '14.0.0.0',

    'depends': ['base','hr_attendance', 'branch', 'vehicle_reservation'],

    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/shift_attendance_view.xml',
        'views/shift_allocation_view.xml',
        'views/shift_management_view.xml',
        'views/rental_views.xml',
    ],

}
