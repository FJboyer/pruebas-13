# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class AccountAdvancedPayment(models.Model):
    _inherit = 'account.advanced.payment'

    def revisar_cambiar_fechas(self):
        fecha_dt = datetime.strptime('2021-01-01', '%Y-%m-%d').date()
        invoices = self.env['account.move'].search([('date', '>=', fecha_dt)
        ])
        for i in invoices:
            if i.date and i.invoice_date:
                if i.invoice_date > i.date:
                    fecha_factura = i.invoice_date.strftime('%Y-%m-%d')
                    fecha= i.date.strftime('%Y-%m-%d')
                    i.write({'invoice_date': fecha, 'date': fecha_factura})