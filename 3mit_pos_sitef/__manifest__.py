# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': '3Mit POS Sitef',
    'version': '1.0',
    'category': 'Sales/Point Of Sale',
    'sequence': 6,
    'summary': 'Integrate your POS with a CliSitef payment terminal',
    'author':'3mit',
    'description': '',
    'data': [
        'views/pos_payment_method_views.xml',
        'views/point_of_sale_assets.xml',
    ],
    'depends': ['point_of_sale'],
    'installable': True,
    'qweb': ['static/src/xml/sitef-api.xml']
}
