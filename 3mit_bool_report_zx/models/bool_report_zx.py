from odoo import models, fields, api

from odoo import api, fields, models, tools, _


class ReportZx(models.Model):
    _inherit = 'pos.session'


    report_x = fields.Boolean('report x', default=False)
