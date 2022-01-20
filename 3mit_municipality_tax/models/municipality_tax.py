# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger("__name__")


class PeriodMonth(models.Model):
    _name = 'period.month'
    _rec_name = 'months_number'

    name = fields.Char(string='Meses')
    months_number = fields.Char(string='Número')


class PeriodYear(models.Model):
    _name = 'period.year'

    name = fields.Char(string='Año')


class MuniWhConcept(models.Model):
    _name = 'muni.wh.concept'

    name = fields.Char(string="Descripción", required=True)
    code = fields.Char(string='Código de actividad', required=True)
    aliquot = fields.Float(string='Alícuota', required=True)
    month_ucim = fields.Char(string='UCIM por mes')
    year_ucim = fields.Char(string='UCIM por año')


class MunicipalityTaxLine(models.Model):
    _name = 'municipality.tax.line'

    concept_id_2 = fields.Many2one('muni.wh.concept', string="Concepto de retención", Copy=False)
    code = fields.Char(string='Código de actividad', store=True)
    aliquot = fields.Float(string='Alícuota')
    base_tax = fields.Float(string='Impuesto base')
    wh_amount = fields.Float(compute="_compute_wh_amount", string='Importe retenido', store=True)
    type = fields.Selection(selection=[('purchase', 'Compra'), ('service', 'Servicio'),
                                       ('dont_apply', 'No aplica')], string='Tipo de transacción')
    municipality_tax_id = fields.Many2one('municipality.tax', string='Municipio')
    move_id = fields.Many2one(string='Asiento contable')
    invoice_id = fields.Many2one('account.move', string='Factura')
    invoice_date = fields.Date(string="Fecha de factura")
    invoice_number = fields.Char(string="Número de factura")
    invoice_ctrl_number = fields.Char(string="Número de control de la factura")

    @staticmethod
    def float_format(valor):
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',', '*')
            result = result.replace('.', ',')
            result = result.replace('*', '.')
        else:
            result = "0,00"
        return result

    """@api.depends('base_tax', 'aliquot')
    def _compute_wh_amount(self):
        # for line in self.act_code_ids:
        # if self.base_tax and self.aliquot:
        _logger.info("\n\n\n\n Se esta realizando el calculo \n\n\n\n")
        retention = ((self.base_tax * self.aliquot) / 100)
        _logger.info("\n\n\n retention %s\n\n\n", retention)
        self.wh_amount = retention
        muni_tax = self.env['municipality.tax'].browse(self.municipality_tax_id.id)
        withheld_amount = self.base_tax
        amount = retention
        if muni_tax:
            muni_tax.write({'withheld_amount': withheld_amount, 'amount': retention})"""

    @api.depends('base_tax', 'aliquot')
    def _compute_wh_amount(self):
        withheld_amount = 0
        amount = 0
        for item in self:        
            _logger.info("\n\n\n\n Se esta realizando el calculo \n\n\n\n")
            retention = ((item.base_tax * item.aliquot) / 100)
            _logger.info("\n\n\n retention %s\n\n\n", retention)
            item.wh_amount = retention
            muni_tax = self.env['municipality.tax'].browse(item.municipality_tax_id.id)

            withheld_amount = withheld_amount+item.base_tax
            amount = amount + item.wh_amount
            if muni_tax:
                muni_tax.write({'withheld_amount': withheld_amount, 'amount': amount})


class MUnicipalityTax(models.Model):
    _name = 'municipality.tax'

    def doc_cedula(self, aux):
        document = ''
        busca_partner = self.env['res.partner'].search([('id', '=', aux)])
        for det in busca_partner:
            if det.company_type == 'person':
                if det.vat:
                    document = det.vat
                else:
                    if det.nationality == 'V' or det.nationality == 'E':
                        document = str(det.nationality) + str(det.identification_id)
                    else:
                        document = str(det.identification_id)
            else:
                if det.vat:
                    document = det.vat
                else:
                    document = 'N/A'
        return document

    @staticmethod
    def float_format2(valor):
        if valor:
            result = '{:,.2f}'.format(valor)
            result = result.replace(',', '*')
            result = result.replace('.', ',')
            result = result.replace('*', '.')
        else:
            result = "0,00"
        return result

    @api.model
    def _type(self):
        if self._context.get('type'):
            return self._context.get('type')

    wh_muni_id = fields.Many2one('account.move', string='Asiento Contable', readonly=True, copy=False)
    name = fields.Char(string='Número de comprobante', default='New')
    state = fields.Selection(selection=[('draft', 'Borrado'), ('posted', 'Publicado'), ('cancel', 'Cancelado')],
                             string='Status', readonly=True, copy=False, tracking=True, default='draft')
    transaction_date = fields.Date(string='Fecha de Transacción', default=datetime.now())
    date_start = fields.Many2one('period.month', string='Fecha de inicio')
    date_end = fields.Many2one('period.year', string='Fecha de finalización')
    rif = fields.Char(string='RIF')
    address = fields.Char(compute="_get_address", string='Dirección')
    partner_id = fields.Many2one('res.partner', string='Partner')
    act_code_ids = fields.One2many('municipality.tax.line', 'municipality_tax_id', string='Código de actividades')
    city = fields.Char(string='Ciudad')
    state_id = fields.Many2one('res.country.state', string='Estado', tracking=True)
    municipality_id = fields.Many2one('res.country.state.municipality', string='Municipio')
    invoice_id = fields.Many2one('account.move', string='Factura')
    amount = fields.Float(string='Monto')
    withheld_amount = fields.Float(string='Importe retenido')
    type = fields.Selection(selection=[('out_invoice', 'Factura de cliente'), ('in_invoice', 'Factura de proveedor'),
                                       ('in_refund', 'Factura rectificativa de proveedor'),
                                       ('out_refund', 'Factura rectificativa de cliente'),
                                       ('in_receipt', 'Nota Debito cliente'), ('out_receipt', 'Nota Debito proveedor')],
                            string="Tipo de factura", store=True, default=_type)
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)
    move_id = fields.Many2one('account.move', string='Id del movimiento')
    invoice_number = fields.Char(string='Nro. de Factura')

    @api.onchange('partner_id')
    def _rif(self):
        if self.partner_id:
            self.rif = self.partner_id.vat

    @api.depends('partner_id')
    def _get_address(self):
        if self.partner_id:
            location = self._get_state_and_city()
            streets = self._get_streets()
            self.address = streets + " " + location
        else:
            self.address = ''

    def _get_state_and_city(self):
        state = ''
        city = ''
        if self.partner_id.state_id:
            state = "Edo." + " " + str(self.partner_id.state_id.name or '')
        if self.partner_id.city:
            city = str(self.partner_id.city or '')
        result = city + " " + state
        return result

    def _get_streets(self):
        street2 = ''
        av = ''
        if self.partner_id.street:
            av = str(self.partner_id.street or '')
        if self.partner_id.street2:
            street2 = str(self.partner_id.street2 or '')
        result = av + " " + street2
        return result

    def get_company_address(self):
        location = ''
        streets = ''
        if self.company_id:
            streets = self._get_company_street()
            location = self._get_company_state_city()
        return streets + " " + location

    def _get_company_street(self):
        street2 = ''
        av = ''
        if self.company_id.street:
            av = str(self.company_id.street or '')
        if self.company_id.street2:
            street2 = str(self.company_id.street2 or '')
        result = av + " " + street2
        return result

    def _get_company_state_city(self):
        state = ''
        city = ''
        if self.company_id.state_id:
            state = "Edo." + " " + str(self.company_id.state_id.name or '')
        if self.company_id.city:
            city = str(self.company_id.city or '')
        result = city + " " + state
        return result

    def action_post(self):
        if not self.transaction_date:
            raise ValidationError("Debe establecer una fecha de Transacción")
        self.state = 'posted'
        nombre_ret_municipal = self.get_name()
        valor = self.registro_movimiento_linea_retencion(nombre_ret_municipal)
        valor.action_post()
        self.wh_muni_id = valor

    def action_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            _logger.info("\n\n\n vals.get.tpye %s \n\n\n", vals.get('type', 'in_invoice'))
            if vals['type'] in ["in_invoice", "in_refund", "in_receipt"]:
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.muni.wh.voucher.number') or '/'
                _logger.info("\n\n\n vals[name] %s \n\n\n", vals['name'])
            else:
                vals['name'] = '00000000'
        return super().create(vals)

    def conv_div_extranjera(self, valor):
        fecha_contable_doc = self.invoice_id.date
        valor_aux = 0
        if self.invoice_id.currency_id.id != self.company_id.currency_id.id:
            tasa = self.env['res.currency.rate'].search([('currency_id', '=', self.invoice_id.currency_id.id),
                                                        ('name', '<=', self.invoice_id.date)], order="name asc")
            for det_tasa in tasa:
                if fecha_contable_doc >= det_tasa.name:
                    valor_aux = det_tasa.rate
            rate = round(1 / valor_aux, 2)  # LANTA
            resultado = valor/rate
        else:
            resultado = valor
        return resultado

    def registro_movimiento_linea_retencion(self, consecutivo_asiento):
        name = consecutivo_asiento
        valores = self.amount
        cuenta_debe = 0
        cuenta_haber = 0
        cuenta_ret_proveedor = None
        cuenta_prove_pagar = None
        cuenta_clien_cobrar = None
        cuenta_ret_cliente = None
        if self.type in ["out_invoice", "out_refund", "out_receipt"]:
            cuenta_ret_cliente = self.partner_id.account_ret_muni_receivable_id.id
            cuenta_ret_proveedor = self.partner_id.account_ret_muni_payable_id.id
            cuenta_clien_cobrar = self.partner_id.property_account_receivable_id.id
            cuenta_prove_pagar = self.partner_id.property_account_payable_id.id

        if self.type in ["in_invoice", "in_refund", "in_receipt"]:
            cuenta_ret_cliente = self.company_id.partner_id.account_ret_muni_receivable_id.id
            cuenta_ret_proveedor = self.company_id.partner_id.account_ret_muni_payable_id.id
            cuenta_clien_cobrar = self.company_id.partner_id.property_account_receivable_id.id
            cuenta_prove_pagar = self.company_id.partner_id.property_account_payable_id.id

        tipo_empresa = self.type
        if tipo_empresa in ["in_invoice", "in_receipt"]:
            cuenta_haber = cuenta_ret_proveedor
            cuenta_debe = cuenta_prove_pagar

        if tipo_empresa == "in_refund":
            cuenta_haber = cuenta_prove_pagar
            cuenta_debe = cuenta_ret_proveedor

        if tipo_empresa in ["out_invoice", "out_receipt"]:
            cuenta_haber = cuenta_clien_cobrar
            cuenta_debe = cuenta_ret_cliente

        if tipo_empresa == "out_refund":
            cuenta_haber = cuenta_ret_cliente
            cuenta_debe = cuenta_clien_cobrar
        journal_lines = [(0, 0, {
            'account_id': cuenta_haber,
            'partner_id': self.partner_id.id,
            'name': name,
            'debit': 0.00,
            'credit': valores,
        }), (0, 0, {
            'account_id': cuenta_debe,
            'partner_id': self.partner_id.id,
            'name': name,
            'debit': valores,
            'credit': 0.00,
        })]

        journal_item = self.env['account.move'].create({
            'ref': "Retencion Impuesto Municipal de la Factura %s" % self.invoice_id.name,
            'journal_id': self.partner_id.purchase_jrl_id.id,
            'line_ids': journal_lines,
            'type': 'entry',
            'state': 'draft'
        })
        return journal_item

    def get_name(self):
        self.ensure_one()
        sequence_code = '3mit_ve_cuenta_retencion_municipal'
        ir_sequence = self.env['ir.sequence'].with_context(force_company=1)
        name = ir_sequence.next_by_code(sequence_code)
        if not name:
            ir_sequence.sudo().create({
                'prefix': 'RET_MUN/',
                'name': 'Localización Venezolana Retenciones Municipales %s' % 1,
                'code': sequence_code,
                'implementation': 'no_gap',
                'padding': 8,
                'number_increment': 1,
                'company_id': 1,
            })
            name = ir_sequence.next_by_code(sequence_code)
        return name
