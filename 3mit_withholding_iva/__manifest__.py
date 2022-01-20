# coding: utf-8
###########################################################################

{
    "name": "Retención IVA las leyes basicas en Venezuela",
    "version": "1.0",
    "author": 'Localizacion Venezolana',
    "category": 'Contabilidad',
    "depends": ['base_vat','base','account','3mit_base_withholdings','web','3mit_grupo_localizacion'],
    'description' : """
Administración de las retenciones de IVA.
===================================================

Colaborador: Maria Carreño
    """,
    #'website': '',
    'data': [
        'security/ir.model.access.csv',
      #  'wizard/wizard_retention_view.xml',
        'view/generate_txt_view.xml',
        'view/account_invoice_view.xml',
        'view/account_view.xml',
        'view/partner_view.xml',
        'view/res_company_view.xml',
        'view/wh_iva_view.xml',
        'report/withholding_vat_report.xml',
    ],
    'installable': True,
    'application': True,
}
