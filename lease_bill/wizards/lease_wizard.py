# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _
from odoo.exceptions import UserError, Warning


class LeaseWizard(models.TransientModel):
    _name = 'lease.wizard'
    _description = 'Lease Wizard'

    amount = fields.Float(string='Amount')
    intr_part = fields.Float(string='Interest Part')
    installment_date_due = fields.Date(string='Installment Due Date')
    interest_months = fields.Integer(string='Interest Months')
    principal_months = fields.Integer(string='Principal Months')

    def create_installments(self):
        if self.amount == 0 or self.interest_months == '':
            raise Warning(_('Amount or Installment Months are Missing'))
        model = self.env.context.get('active_model')
        rec = self.env[model].browse(self.env.context.get('active_id'))
        date = self.installment_date_due
        for i in range(0, self.interest_months - self.principal_months):
            date = date + relativedelta(months=1)
            rec.write({
                'lease_bill_lines': [(0, 0, {
                    'date_account': date.today(),
                    'date_due': date,
                    'int_part': self.intr_part,
                    'due_total': self.intr_part,
                    'prin_balance': self.amount,
                })]
            })

        amount = self.amount
        for i in range(0, self.principal_months):
            annum_perc = (rec.kibor + rec.interest_rate) / 100
            annum_amnt = (round(amount, 0)) * annum_perc
            mont_amnt = annum_amnt / 12
            amount = amount - (amount/(rec.installment_remain-i))
            date = date + relativedelta(months=1)
            rec.write({
                'lease_bill_lines': [(0, 0, {
                    'date_account': date.today(),
                    'date_due': date,
                    'prin_part': self.amount / rec.installment_remain,
                    'int_part': round(mont_amnt, 0),
                    'prin_balance': round(amount, 0),
                    'due_total': round(((self.amount / rec.installment_remain) + mont_amnt), 0),
                })]
            })
        rec.is_installment = True
