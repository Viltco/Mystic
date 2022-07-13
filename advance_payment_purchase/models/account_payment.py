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
        self.move_id._post(soft=False)
