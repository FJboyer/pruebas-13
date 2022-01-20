# coding: utf-8
###########################################################################

##############################################################################
{
    "name": "Modificaciones para impresora fiscal",
    "version": "1.0",
    "author": "3mit",
    "license": "AGPL-3",
    "category": "ventas",
    #"website": "",
    "colaborador":"yorman",
    'depends': ['stock_account', 'point_of_sale'],

    'demo': [
    ],
    "data": [
        'views/reemprimir.xml',
        'security/ir.model.access.csv',
        #'views/menus_reportes_view.xml',
        #'reports/report_zeta.xml',

    ],
    'test': [

    ],
    "installable": True,
    'application': True,

}
