# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta


class RecurringBillType(models.Model):
    _name = 'recurring.bill.type'
    _description = 'Recurring Bill Type'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')
    recurring_interval = fields.Integer(string='Recurring Interval')
    is_asset_status = fields.Boolean(string='Confirm Asset Status')
    payment_schedule = fields.Selection([
        ('day', 'Day'),
        ('month', 'Month'),
        ('year', 'Year'),
    ], string='Payment Schedule')


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    recurring_bill_type_id = fields.Many2one('recurring.bill.type', string='Recurring Type')

    def action_create_bill(self):
        record = self.env['account.move'].search([])
        for rec in record:
            if rec.move_type == 'in_invoice':
                if rec.recurring_bill_type_id and rec.state == 'posted':
                    # date = rec.invoice_date
                    new_bill = rec.copy()
                    new_bill.invoice_date = rec.invoice_date + relativedelta(months=rec.recurring_bill_type_id.recurring_interval)
                    new_bill.date = rec.invoice_date + relativedelta(months=rec.recurring_bill_type_id.recurring_interval)
                    # if rec.recurring_bill_type_id.payment_schedule == 'month':
                    #     date = date + relativedelta(months=rec.recurring_bill_type_id.recurring_interval)
                    rec.recurring_bill_type_id = []

    def action_post(self):
        flag = False
        for record in self:
            for line in record.invoice_line_ids:
                if not line.assets_id.state == 'open':
                    flag = True
                if flag == True:
                    raise Warning(_('Please Select the Valid Running Assets in Lines'))
                else:
                    rec = super(AccountMoveInh, self).action_post()
                    return rec


class AccountMoveLineInh(models.Model):
    _inherit = 'account.move.line'

    assets_id = fields.Many2one('account.asset', string='Asset', force_save='1')

