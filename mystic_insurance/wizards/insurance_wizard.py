# -*- coding: utf-8 -*-

from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _
from odoo.exceptions import UserError, Warning


class InsuranceWizard(models.TransientModel):
    _name = 'insurance.wizard'
    _description = 'Insurance Wizard'

    date = fields.Date(string='Date', default=date.today())
    partner_id = fields.Many2one('res.partner', string='Vendor', domain=lambda self: [("supplier_rank", ">=", 1)])
    journal_id = fields.Many2one('account.journal', string='Journal', domain=lambda self: [("type", "=", 'purchase')])
    product_id = fields.Many2one('product.product', string='Insurance Expense', domain=lambda self: [("type", "=", 'service')])

    fleet_ids = fields.Many2many('fleet.insurance.line')

    def create_bills(self):
        lst = []
        for recs in self.fleet_ids:
            lst.append(recs.branch_id.id)
        ele = lst[0]
        chk = True
        for item in lst:
            if ele != item:
                chk = False
                break
        if (chk == False):
            raise UserError(_('Please Select One Branch Only'))
        # model = self.env.context.get('active_model')
        # records = self.env[model].browse(self.env.context.get('active_id'))
        line_val = []
        for record in self.fleet_ids:
            if record.date_from > self.date and record.date_to < self.date:
                raise UserError(_('Date Not in Range' + ' ' + str(self.date)))
            # if record.date_from <= self.date and record.date_to >= self.date:
                # raise UserError(_('Date in Range' + ' ' + str(self.date)))
            else:
                line_val.append((0, 0, {
                    'product_id': self.product_id.id,
                    'analytic_tag_ids': record.fleet_vehicle_id.branch_id.analytical_account_tag_id,
                    'analytic_account_id': record.fleet_vehicle_id.analytical_account_id.id,
                    'branch_id': record.branch_id.id,
                    'price_unit': record.amount_subtotal,
                }))
                vals = {
                    'partner_id': self.partner_id.id,
                    'journal_id': self.journal_id.id,
                    'invoice_date': self.date,
                    'date': self.date,
                    'invoice_date_due': self.date,
                    'branch_id': record.branch_id.id,
                    'move_type': 'in_invoice',
                    'company_id': self.env.company.id,
                    'invoice_line_ids': line_val
                }
        record = self.env['account.move'].create(vals)
            # elif record.date_from > self.date and record.date_to < self.date:
            #     raise UserError(_('Date Not in Range' + ' ' + str(self.date)))
            # record = self.env['account.move'].create(vals)
