# -*- coding: utf -*-
from odoo import fields, models


class Partners(models.Model):
    _inherit = 'res.partner'

    muni_wh_agent = fields.Boolean(string='Agente de retención', help='Verdadero si el partner es agente de retención'
                                                                      ' municipal.')
    purchase_jrl_id = fields.Many2one('account.journal', string='Diario de compras')
    sale_jrl_id = fields.Many2one('account.journal', string='Diario de ventas')
    account_ret_muni_receivable_id = fields.Many2one('account.account', string='Cuenta de retención clientes')
    account_ret_muni_payable_id = fields.Many2one('account.account', string='Cuenta de retención proveedores')
    nit = fields.Char(string='NIT', help='Número antiguo de identificación del impuesto reemplazado por el RIF actual.')
    econ_act_license = fields.Char(string='License number', help='Número de licencia para la actividad económica.',
                                   required=True)
    nifg = fields.Char(string='NIFG', help='Número asignado por el Satrin.', required=True)
