from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AdvancePaymentWizard(models.TransientModel):
    _name = 'lease.payment.wizard'
    _description = 'Lease Payment'

    lease_lines = fields.Many2one('lease.bill.line')
    amount = fields.Float('Amount')

    def default_journal_id(self):
        journal = self.env['account.journal'].search([('name', '=', 'Cash')])
        return journal.id

    journal_id = fields.Many2one('account.journal', default=default_journal_id)

    def default_currency_id(self):
        currency = self.env['res.currency'].search([('name', '=', 'PKR')])
        return currency.id

    currency_id = fields.Many2one('res.currency', default=default_currency_id)

    def default_payment_method_id(self):
        method = self.env['account.payment.method'].search([('name', '=', 'Manual')], limit=1)
        return method.id

    payment_method_id = fields.Many2one('account.payment.method', default=default_payment_method_id)
    ref = fields.Char('Reference')
    partner_id = fields.Many2one('res.partner', string='Customer/Vendor')
    destination_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Destination Account',
        store=True, readonly=False,
        domain="[('user_type_id.type', 'in', ('receivable', 'payable'))]")

    def create_data(self):
        # print('payment')
        # model = self.env.context.get('active_model')
        # record = self.env[model].browse(self.env.context.get('active_id'))
        # print(model)
        # print(record)
        for rec in self:
            print('yesssssssssssssssssssssssss')
            vals = {
                'partner_type': 'supplier',
                'journal_id': rec.journal_id.id,
                'partner_id': rec.partner_id.id,
                'date': datetime.today().date(),
                'amount': rec.amount,
                # 'currency_id': rec.currency_id.id,
                'ref': rec.ref,
                'state': 'draft',
            }
            payment = self.env['account.payment'].create(vals)

