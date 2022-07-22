# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from datetime import date


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    lease_bill_id = fields.Many2one('lease.bill', string='Lease Bill')
    due_date = fields.Date(string='Payment Due Date', compute='_compute_due_date')

    @api.depends('lease_bill_id')
    def _compute_due_date(self):
        for rec in self:
            if rec.line_ids:
                rec.due_date = rec.line_ids[-1].date_maturity
            else:
                rec.due_date = False

    # def test_fun(self):
    #     for rec in self:
    #         if 'Days' in rec.invoice_payment_term_id.name:
    #             days = rec.invoice_payment_term_id.name
    #             days = days.split(' ')[0]
    #         elif 'Months' in rec.invoice_payment_term_id.name:
    #             days = rec.invoice_payment_term_id.name
    #             days = days.split(' ')[0]
    #             days = int(days) * 30
    #         else:
    #             pass
    #         date_1 = self.invoice_date + timedelta(days=int(days))
    #         print(date_1)
    #         final = date_1.strftime('%m-%d-%y')
    #         print(final)
