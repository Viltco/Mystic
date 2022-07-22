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
    branch_id = fields.Many2one('res.branch')
    lines_list = fields.Char()

    def create_data(self):
        move_ids = []
        for l in str(self.lines_list).split(' '):
            move_ids.append(l.replace("]", '').replace("[", '').replace("'", '').replace(',',''))
        print(move_ids)
        record = self.env['lease.bill.line'].search([('move_id.name', 'in', move_ids)])
        # total_interest = 0
        interest_lines = []
        for rec in record:
            if rec.move_id:
                if rec.prin_part == 0.0:
                    interest_lines.append((0, 0, {
                        'invoice_id': rec.move_id.id,
                        'origin': '',
                        'date_invoice': datetime.today(),
                        'date_due': datetime.today(),
                        'amount_total': rec.int_part,
                        'reconcile_amount': rec.int_part,
                    }))
                else:
                    interest_lines.append((0, 0, {
                        'invoice_id': rec.move_id.id,
                        'origin': '',
                        'date_invoice': datetime.today(),
                        'date_due': datetime.today(),
                        'amount_total': rec.int_part,
                        'reconcile_amount': rec.int_part,
                    }))
                    interest_lines.append((0, 0, {
                        'invoice_id': rec.bill_id.id,
                        'origin': '',
                        'date_invoice': datetime.today(),
                        'date_due': datetime.today(),
                        'amount_total': rec.prin_part,
                        'reconcile_amount': rec.prin_part,
                    }))
        vals = {
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'journal_id': self.journal_id.id,
            'partner_id': self.partner_id.id,
            'date': datetime.today().date(),
            # 'amount': self.amount,
            'ref': self.ref,
            'state': 'draft',
            'branch_id': self.branch_id.id,
            'payment_invoice_ids':interest_lines
        }
        payment = self.env['account.payment'].create(vals)
        # #     payment._onchange_to_get_vendor_invoices()
