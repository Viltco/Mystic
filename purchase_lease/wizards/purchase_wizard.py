# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _
from odoo.exceptions import UserError, Warning


class RegisterPaymentWizard(models.TransientModel):
    _name = 'register.payment.wizard'
    _description = 'Schedule Payment'

    amount = fields.Float(string='Amount')
    no_of_days = fields.Integer(string='No of Installment')
    down_payemnt = fields.Float(string='Down Payment')
    is_check = fields.Boolean(string='Is Check')
    date_due = fields.Date(string='Installment Due Date')
    down_payemnt_date_due = fields.Date(string='Due Date')
    installment_interval = fields.Integer(string='Installment Interval')

    payment_schedule = fields.Selection([
        ('day', 'Day'),
        ('month', 'Month'),
        ('year', 'Year')
    ], string='Payment Schedule')

    def create_installments(self):
        if self.no_of_days == 0 or self.payment_schedule == '':
            raise Warning(_('Please Select No of Days or Payment Schedule'))
        model = self.env.context.get('active_model')
        rec = self.env[model].browse(self.env.context.get('active_id'))
        for line in rec.installment_lines:
            if line.payment_status == 'unpaid':
                line.unlink()
        if self.down_payemnt != 0:
            rec.write({
                'installment_lines': [(0, 0, {
                    'partner_id': rec.partner_id.id,
                    'bill_ref_id': rec.id,
                    'date_due': self.down_payemnt_date_due,
                    'amount': self.down_payemnt,
                })]
            })
        date = self.date_due
        for i in range(0, self.no_of_days):
            if self.payment_schedule == 'day':
                date = date + relativedelta(days=self.installment_interval)
            elif self.payment_schedule == 'month':
                date = date + relativedelta(months=self.installment_interval)
            elif self.payment_schedule == 'year':
                date = date + relativedelta(years=self.installment_interval)
            rec.write({
                'installment_lines': [(0, 0, {
                    'partner_id': rec.partner_id.id,
                    'bill_ref_id': rec.id,
                    'date_due': date,
                    'amount': (self.amount - self.down_payemnt)/self.no_of_days,
                })]
            })

        rec.is_installment = True

