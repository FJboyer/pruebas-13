# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
import requests

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('sitef', 'Sitef')]

    sitef_restApi = fields.Char('CliSitef Terminal Url',default='http://localhost:5000')
    sitef_methodType=fields.Selection([('2', 'Tarjeta de Débito'), ('3', 'Tarjeta de Crédito')], default='3', string="Tipo")
    
    ##
    def getSitefScript(self):
        for rec in self:
            if rec.use_payment_terminal=='sitef':
                url=f'{rec.sitef_restApi}/sitef.js'
                try:
                    rs=requests.get(url)
                    rec.sitef_script=rs.text+f'; return getSitef("{rec.sitef_restApi}",$);'
                except:
                    rec.sitef_script=None
            else:
                rec.sitef_script=''
    sitef_script=fields.Char(compute=getSitefScript, store=False)
