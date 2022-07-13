# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from datetime import date


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    installment_lines = fields.One2many('installment.line', 'installment_move_id')
    is_installment = fields.Boolean(string='Is Installment')

    def action_create_installment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Schedule Installments',
            'view_id': self.env.ref('purchase_lease.view_register_payment_wizard_form', False).id,
            'context': {'default_amount': self.amount_total, 'default_date_due': self.invoice_date, 'default_down_payemnt_date_due': self.invoice_date},
            'target': 'new',
            'res_model': 'register.payment.wizard',
            'view_mode': 'form',
        }

    def action_update_payment(self):
        lines = self.installment_lines.filtered(lambda r: r.payment_status == 'unpaid')
        tot = sum(lines.mapped('amount'))
        print(tot)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Update Installments',
            'view_id': self.env.ref('purchase_lease.view_register_payment_wizard_form', False).id,
            'context': {'default_amount': tot, 'default_is_check': True, 'default_date_due': self.invoice_date},
            'target': 'new',
            'res_model': 'register.payment.wizard',
            'view_mode': 'form',
        }


class InstallmentLines(models.Model):
    _name = 'installment.line'
    _description = 'Installment Line'

    installment_move_id = fields.Many2one('account.move')
    payment_id = fields.Many2one('account.payment', string='Pmt Ref', domain=lambda self: [("state", "=", 'posted')])
    partner_id = fields.Many2one('res.partner', string='Vendor')
    bill_ref_id = fields.Many2one('account.move', string='Bill Reference', domain=lambda self: [("move_type", "=", 'in_invoice')])
    date_due = fields.Date(string='Due Date')
    amount = fields.Float(string='Amount')
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ], string='Payment Status', default='unpaid')

    def action_create_payment(self):
        for rec in self:
            vals = {
                'partner_type': 'supplier',
                'partner_id': rec.partner_id.id,
                'amount': rec.amount,
                'payment_type': 'outbound',
                'installment_id': rec.id,
                'state': 'draft',
            }
            payment = self.env['account.payment'].create(vals)
            self.payment_id = payment.id

    def action_post_status(self):
        if (self.payment_id.amount == self.amount) and (self.partner_id == self.payment_id.partner_id):
            print('passed')
            self.payment_status = 'paid'


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    installment_id = fields.Many2one('installment.line', string='Installment Reference')

    def action_post(self):
        res = super(AccountPaymentInh, self).action_post()
        if self.installment_id:
            self.installment_id.payment_status = 'paid'
        return res


