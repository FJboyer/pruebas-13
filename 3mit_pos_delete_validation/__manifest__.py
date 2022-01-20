# -*- coding: utf-8 -*-
{
    'name': "3mit_pos_delete_validation",

    'summary': """
        Desarrollo para borrar y/o modificar productos en POS
    """,

    'description': """
        Desarrollo para borrar y/o modificar productos en POS
    """,

    'author': "3mit",
    'website': "http://www.3mit.dev",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'views/views.xml',
        'views/templates.xml',
        'static/src/xml/pos_code_admin_pos.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': ['static/src/xml/3mit_pos_delete_validation.xml']
}
