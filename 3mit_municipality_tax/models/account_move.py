# -*- coding: utf-8 -*-
import logging
from odoo import fields, models

_logger = logging.getLogger('__name__')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    concept_id_2 = fields.Many2one('muni.wh.concept', string='Impuesto municipal')

    def _check_balanced(self):
        # Assert the move is fully balanced debit = credit. An error is raised if it's not the case.
        moves = self.filtered(lambda move: move.line_ids)
        if not moves:
            return

        # /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
        # are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
        # It happens as the ORM makes the create with the 'no_recompute' statement.
        self.env['account.move.line'].flush(['debit', 'credit', 'move_id'])
        self.env['account.move'].flush(['journal_id'])
        self._cr.execute('''
            SELECT line.move_id, ROUND(SUM(debit - credit), currency.decimal_places)
            FROM account_move_line line
            JOIN account_move move ON move.id = line.move_id
            JOIN account_journal journal ON journal.id = move.journal_id
            JOIN res_company company ON company.id = journal.company_id
            JOIN res_currency currency ON currency.id = company.currency_id
            WHERE line.move_id IN %s
            GROUP BY line.move_id, currency.decimal_places
            HAVING ROUND(SUM(debit - credit), currency.decimal_places) != 0.0;
        ''', [tuple(self.ids)])

        # query_res = self._cr.fetchall()
        # if query_res:
        #     ids = [res[0] for res in query_res]
        #     sums = [res[1] for res in query_res]


class AccountMove(models.Model):
    _inherit = 'account.move'

    wh_muni_id = fields.Many2one('municipality.tax', string='Retención del impuesto municipal', readonly=True, copy=False)

    def conv_div_nac(self, valor):
        fecha_contable_doc = self.date
        valor_aux = 0

        if self.currency_id.id != self.company_id.currency_id.id:
            tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.currency_id.id),
                                                        ('name', '<=', self.date)], order="name asc")
            for det_tasa in tasa:
                if fecha_contable_doc >= det_tasa.name:
                    valor_aux = det_tasa.rate
            rate = round(1 / valor_aux, 2)  # LANTA
            resultado = valor * rate
        else:
            resultado = valor
        return resultado

    def _create_muni_wh_voucher(self):
        muni_wh = self.env['municipality.tax']
        _logger.info("""\n\n\n Hola se esta ejecutando el action_post de la retencion municipal\n\n\n""")
        res = []
        for item in self.invoice_line_ids:
            base_impuesto = item.price_subtotal
            if item.concept_id_2.aliquot > 0:
                res.append((0, 0, {
                    'code': item.concept_id_2.code,
                    'aliquot': item.concept_id_2.aliquot,
                    'concept_id_2': item.concept_id_2.id,
                    'base_tax': self.conv_div_nac(base_impuesto),
                    'invoice_id': self.id,
                    'invoice_date': self.date,
                    'invoice_number': self.supplier_invoice_number,
                    'invoice_ctrl_number': self.nro_ctrl,
                }))
        _logger.info("\n\n\n res %s \n\n\n\n", res)
        year_id = self.env['period.year'].search([('name', '=', str(self.date.year))])
        vals = {
            'partner_id': self.partner_id.id,
            'rif': self.partner_id.vat,
            'invoice_id': self.id,
            'act_code_ids': res,
            'type': self.type,
            'date_start': self.date.month,
            'date_end': year_id.id
        }
        _logger.info("\n\n\n vals %s \n\n\n", vals)
        muni_tax = muni_wh.create(vals)
        _logger.info("\n\n\n muni %s\n\n\n", muni_tax)
        self.write({'wh_muni_id': muni_tax.id})

    def actualiza_voucher_wh(self):
        cursor_municipality = self.env['municipality.tax'].search([('id', '=', self.wh_muni_id.id)])
        for det in cursor_municipality:
            self.env['municipality.tax'].browse(det.id).write({
                'type': self.type,
                'invoice_number': self.supplier_invoice_number
            })

    def action_post(self):
        invoice = super().action_post()
        _logger.info("\n\n\n\n action_post de Impuestos municipales \n\n\n\n")
      
        if self.partner_id.muni_wh_agent or self.company_id.partner_id.muni_wh_agent:
            bann = self.verifica_exento_muni()
            if bann > 0:
                if not self.wh_muni_id:
                    self._create_muni_wh_voucher()
                self.actualiza_voucher_wh()
                self.unifica_alicuota_iguales()
        return invoice

    def verifica_exento_muni(self):
        acum = 0
        puntero_move_line = self.env['account.move.line'].search([('move_id', '=', self.id)])
        for det_puntero in puntero_move_line:
            acum = acum+det_puntero.concept_id_2.aliquot
        return acum

    def unifica_alicuota_iguales(self):
        if self.type in ['in_invoice', 'in_refund', 'in_receipt']:
            type_tax_use = 'purchase'
        if self.type in ['out_invoice', 'out_refund', 'out_receipt']:
            type_tax_use = 'sale'
        lista_impuesto = self.env['muni.wh.concept'].search([])
        for det_tax in lista_impuesto:
            lista_mov_line = self.env['municipality.tax.line'].search([('invoice_id', '=', self.id),
                                                                       ('concept_id_2', '=', det_tax.id)])
            code = None
            aliquot = None
            invoice_id = None
            invoice_number = None
            municipality_tax_id = None
            invoice_ctrl_number = None
            type_tax = None
            concept_id_2 = None
            base_tax = 0
            wh_amount = 0
            if lista_mov_line:
                for det_mov_line in lista_mov_line:                
                    base_tax = base_tax+det_mov_line.base_tax
                    wh_amount = wh_amount+det_mov_line.wh_amount
                    code = det_mov_line.code
                    aliquot = det_mov_line.aliquot
                    invoice_id = det_mov_line.invoice_id.id
                    invoice_number = det_mov_line.invoice_number
                    municipality_tax_id = det_mov_line.municipality_tax_id.id
                    invoice_ctrl_number = det_mov_line.invoice_ctrl_number
                    type_tax = det_mov_line.type
                    concept_id_2 = det_mov_line.concept_id_2.id
                lista_mov_line.unlink()
                move_obj = self.env['municipality.tax.line']
                valor = {
                    'code': code,
                    'aliquot': aliquot,
                    'invoice_id': invoice_id,
                    'invoice_number': invoice_number,
                    'municipality_tax_id': municipality_tax_id,
                    'invoice_ctrl_number': invoice_ctrl_number,
                    'base_tax': base_tax,
                    'wh_amount': wh_amount,
                    'type': type_tax,
                    'concept_id_2': concept_id_2
                }
                move_obj.create(valor)
