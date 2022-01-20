{
    "name": "Gestión de retenciones leyes venezolanas",
    "version": "1.0",
    "author": "Localizacion Venezolana",
    "license": "AGPL-3",
   # "website": "http://vauxoo.com",
    "category": 'Contabilidad',
    "depends": [ 'account',
        'base_vat',
        'account_accountant', 'base', '3mit_account_fiscal_requirements','3mit_grupo_localizacion'],
    'data': [
        'security/ir.model.access.csv',
        'view/base_withholding_view.xml',
    ],
    'installable': True,
    'application': True,
}