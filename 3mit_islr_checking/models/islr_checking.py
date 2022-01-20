# -*- coding: utf-8 -*-

from odoo import models


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        if self.islr_wh_doc_id and self.islr_wh_doc_id.state != 'cancel':
           self.islr_wh_doc_id = None
        return super(AccountMoveInherit, self).action_post()
