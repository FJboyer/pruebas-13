# -*- coding: utf-8 -*-
from odoo import fields, models


class Company(models.Model):
    _inherit = 'res.company'

    nit = fields.Char(string='NIT', help='Número antiguo de identificación del impuesto reemplazado por el RIF actual.')
    econ_act_license = fields.Char(string='License number', help='Número de licencia para la actividad económica.',
                                   required=True)
    nifg = fields.Char(string='NIFG', help='Número asignado por el Satrin.', required=True)
