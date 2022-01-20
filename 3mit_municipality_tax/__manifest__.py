# -*- coding: utf-8 -*-
{
    'name': 'Impuestos municipales para la Localización venezolana',

    'summary': """
        Módulo que contiene los impuestos auxiliares para la localización de Venezuela.""",

    'description': """
        * Menú action en Contabilidad.
        * Vistas form y tree para registro de impuestos municipales.\n
        Colaborador: Kleiver Pérez.
    """,

    'version': '1.2.1',
    'author': '3MIT',
    'description': 'Municipal Taxes',
    'category': 'Accounting',
    'website': "https://www.3mit.dev/",
    'depends': ['account_accountant', 'base', '3mit_withholding_iva', '3mit_ve_dpt'],
    'data': [
        'security/ir.model.access.csv',
        'data/muni.wh.concept.csv',
        'data/seq_muni_tax_data.xml',
        'data/period.month.csv',
        'data/period.year.csv',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
        'views/municipality_tax_views.xml',
        'report/report_municipal_tax.xml',
        'views/res_company_views.xml',
        ],
    'installable': True,
    'application': True,
}
