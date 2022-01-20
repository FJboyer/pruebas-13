# coding: utf-8
###########################################################################

##############################################################################
{
    "name": "Agrega precio y Pagos en $ en punto de venta",
    "version": "1.0",
    "author": "3mit",
    "license": "AGPL-3",
    "category": "ventas",
    #"website": "",
    "colaborador":"Ing. Yorman Pineda",
    'depends': ['stock_account', 'web_editor', 'digest', 'point_of_sale','3mit_aux_product'],

    'demo': [
    ],
    "data": [
        #'security/ir.model.access.csv',
        'views/point_of_sale.xml',
        'views/bool_metodopagos_view.xml',

    ],
    'test': [

    ],
    'installable': True,
    'active': True,
    'qweb': ['static/src/xml/pos.xml'],

}
