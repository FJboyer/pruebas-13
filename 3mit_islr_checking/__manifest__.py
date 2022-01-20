# -*- coding: utf-8 -*-
{
    'name': "Chequeo documento ISLR",

    'summary': """
        Chequea si una una factura tiene retención de ISLR.
        """,

    'description': """
        Realiza el chequeo de factura y verifica si tiene un ISLR asociado.\n
        Si se le modifican los valores en el account.move.line, actualiza el documento de retención del ISLR asociado.\n\n
        Colaborador: Kleiver Pérez.
    """,

    'author': "3MIT",
    'website': "https://www.3mit.dev/",
    'category': 'Tax',
    'version': '1.1',
    'depends': ['base', 'account', '3mit_withholding_islr'],

    'data': [

    ],
    'demo': [

    ],
}
