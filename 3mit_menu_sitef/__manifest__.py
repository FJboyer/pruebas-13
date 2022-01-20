# -*- coding: utf-8 -*-
{
    'name': "Menu para funciones generales de Sitef",
    'summary': "Menu Sitef",
    'description': "Elaborado por: Ing Yorman Pineda",
    'version': '1.0',
    'author': '3mit',
    'category': 'Tools',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_sitef.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'qweb': ['static/xml/dialog.xml']
}
