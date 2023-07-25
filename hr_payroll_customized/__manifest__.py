# -*- coding: utf-8 -*-
{
    'name': 'HR Payroll Customized',
    'version': '1.0.0',
    'sequence': -1,
    'summary': 'HR Payroll',
    'author': 'Anakut Digital',
    'category': 'Technical',
    'description': """
HR Payroll Customized By Anakut
==================================

""",
    'depends': ['hr_payroll', 'hr_attendance_customized', 'hr_holidays'],
    'data': [
        'views/res_config_settings_views.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'assets': {},
    'license': 'LGPL-3',
}
