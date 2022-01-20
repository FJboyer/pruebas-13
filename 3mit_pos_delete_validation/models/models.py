# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompanyForm(models.Model):
    _inherit = 'res.company'    
    code_pos = fields.Char('Código POS')
    delete_pass_dev = fields.Boolean('Validación al borrar productos')

# class 3mit_pos_delete_validation(models.Model):
#     _name = '3mit_pos_delete_validation.3mit_pos_delete_validation'
#     _description = '3mit_pos_delete_validation.3mit_pos_delete_validation'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
