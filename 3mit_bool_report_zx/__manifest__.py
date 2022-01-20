# -*- coding: UTF-8 -*-

{
    "name": "Agrega booleno en la sesion de punto de venta",
    "version": "1.0",
    "author": "Maria Carreño",
    'depends' : [#"hr",
                 "base","base_vat","point_of_sale"],
    "data": [
        'security/ir.model.access.csv',
        'view/bool_report_view.xml',
             ],
    'category': 'punto de venta',
    "description": """
     Agrega el campo booleano a la sesion de punto de venta
    """,
    'installable': True,
    'application': True,
}
