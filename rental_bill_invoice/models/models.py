# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveInherited(models.Model):
    _inherit = 'account.move'

    def get_amount_in_words(self):
        if self.amount_total:
            text = self.currency_id.amount_to_text(self.amount_total)
            return text.title()
        else:
            return 'Zero'

    def get_date(self, date):
        return str(date).split(' ')[0]
