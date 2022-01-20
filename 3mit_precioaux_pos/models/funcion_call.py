# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import itertools
import logging
from odoo.tools import float_is_zero
from odoo.exceptions import UserError,Warning
from odoo import api, fields, models, tools, _
_logger = logging.getLogger(__name__)

class MetodosPago(models.Model):
    _inherit = "pos.payment.method"
    dolar_active = fields.Boolean(default=False)

class ProductTemplateInherit(models.Model):
    _inherit = "res.currency"

    @api.model
    def print_barcode(self):
        busqueda = self.env['res.currency.rate'].search([], order='id desc')
        if busqueda:
            rate = busqueda[0].rate
            return rate

class CurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    _sql_constraints = [
        ('unique_name_per_day', 'Check(1=1)', 'Only one currency rate per day allowed!'),
        ('currency_rate_check', 'CHECK (rate>0)', 'The currency rate must be strictly positive.'),
    ]

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _process_payment_lines(self, pos_order, order, pos_session, draft):
        """Create account.bank.statement.lines from the dictionary given to the parent function.

        If the payment_line is an updated version of an existing one, the existing payment_line will first be
        removed before making a new one.
        :param pos_order: dictionary representing the order.
        :type pos_order: dict.
        :param order: Order object the payment lines should belong to.
        :type order: pos.order
        :param pos_session: PoS session the order was created in.
        :type pos_session: pos.session
        :param draft: Indicate that the pos_order is not validated yet.
        :type draft: bool.
        """
        prec_acc = order.pricelist_id.currency_id.decimal_places

        order_bank_statement_lines= self.env['pos.payment'].search([('pos_order_id', '=', order.id)])
        order_bank_statement_lines.unlink()
        diferencia = order.amount_total - order.amount_paid
        order.amount_paid = order.amount_total
        excedente = order.amount_return
        order.amount_return = 0
        pos_order['amount_return'] = 0
        for payments in pos_order['statement_ids']:
            if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
                busqueda = self.env['pos.payment.method'].search([('id', '=', payments[2]['payment_method_id'])])
                if busqueda.dolar_active == True:
                    payments[2]['amount'] = payments[2]['amount'] + diferencia - excedente
                    diferencia = excedente = 0
                order.add_payment(self._payment_fields(order, payments[2]))

        order.amount_paid = sum(order.payment_ids.mapped('amount'))

        if not draft and not float_is_zero(pos_order['amount_return'], prec_acc):
            cash_payment_method = pos_session.payment_method_ids.filtered('is_cash_count')[:1]
            if not cash_payment_method:
                raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
            return_payment_vals = {
                'name': _('return'),
                'pos_order_id': order.id,
                'amount': -pos_order['amount_return'],
                'payment_date': fields.Date.context_today(self),
                'payment_method_id': cash_payment_method.id,
            }
            order.add_payment(return_payment_vals)
