# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    is_advance_pay = fields.Boolean(string='Is Advance Payment')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order',
                                        domain="[('partner_id', '=', partner_id)]")
    advance_amount = fields.Float(string='Advance Amount', compute='_compute_purchase_order_id')

    @api.depends('purchase_order_id')
    def _compute_purchase_order_id(self):
        records = self.env['account.payment'].search(
            ['&', ('state', '=', 'posted'), ('is_advance_pay', '=', True),
             ('purchase_order_id', '=', self.purchase_order_id.id)])
        total = 0
        for rec in records:
            total += rec.amount
        ad_amount = self.purchase_order_id.advance_amount - total
        self.advance_amount = ad_amount

    def check_amount(self):
        records = self.env['account.payment'].search(
            ['&', ('state', '=', 'posted'), ('is_advance_pay', '=', True),
             ('purchase_order_id', '=', self.purchase_order_id.id)])
        total = 0
        for rec in records:
            total += rec.amount
        ad_amount = self.purchase_order_id.advance_amount - total
        self.advance_amount = ad_amount
        total += self.amount
        if total > self.purchase_order_id.advance_amount:
            raise UserError('Advance has already been paid')
        print(total)

    def button_approved(self):
        print('action post')
        if self.purchase_order_id:
            self.check_amount()
        records = self.env['account.payment'].search(
            ['&', ('state', '=', 'posted'), ('is_advance_pay', '=', True),
             ('purchase_order_id', '=', self.purchase_order_id.id)])
        total = 0
        for rec in records:
            total += rec.amount
        ad_amount = self.purchase_order_id.advance_amount - total
        self.advance_amount = ad_amount
        total += self.amount
        if total == self.purchase_order_id.advance_amount:
            self.purchase_order_id.payment_state = 'paid'
            print('paid')
        if total < self.purchase_order_id.advance_amount:
            self.purchase_order_id.payment_state = 'partial'
            print('partial')
        self.write({
            'state': 'posted'
        })
        for payment in self:
            # if payment.payment_invoice_ids:
            #     if payment.amount < sum(payment.payment_invoice_ids.mapped('reconcile_amount')):
            #         raise UserError(_("stop the function."))
            print('=====payment method_id====',payment.payment_method_id)
            for line_id in payment.payment_invoice_ids:
                if not line_id.reconcile_amount:
                    continue
                if line_id.amount_total <= line_id.reconcile_amount:
                    self.ensure_one()
                    if payment.payment_type == 'inbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.credit > 0)
                        lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.reconcile()
                    elif payment.payment_type == 'outbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.debit > 0)
                        lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.reconcile()
                else:
                    self.ensure_one()
                    if payment.payment_type == 'inbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.credit > 0)
                        lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.with_context(amount=line_id.reconcile_amount).reconcile()
                    elif payment.payment_type == 'outbound':
                        lines = payment.move_id.line_ids.filtered(lambda line: line.debit > 0)
                        lines += line_id.invoice_id.line_ids.filtered(lambda line: line.account_id == lines[0].account_id and not line.reconciled)
                        lines.with_context(amount=line_id.reconcile_amount).reconcile()
        self.move_id._post(soft=False)

