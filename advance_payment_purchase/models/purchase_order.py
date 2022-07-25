# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'
    bpo = fields.Char(string='PBO')
    is_advance_payment = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Is Advance Payment')
    advance_amount = fields.Float(string='Advance Amount')
    payment_state = fields.Selection(selection=[
        ('not_app', 'N/A'),
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid')
    ], string='Advance Status')

    def get_payments(self):
        print('yes')
        return {
            'name': _('Payments'),
            'domain': ['&', ('purchase_order_id', '=', self.id), ('state', 'in', ['draft', 'posted']),
                       ('is_advance_pay', '=', True)],
            'context': {'default_partner_type': 'supplier'},
            'view_type': 'form',
            'res_model': 'account.payment',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    @api.onchange('is_advance_payment')
    def _onchange_is_advance_payment(self):
        records = self.env['account.payment'].search(
            ['&', ('state', '=', 'posted'), ('is_advance_pay', '=', True), ('purchase_order_id', '=', self.id)])
        if self.is_advance_payment == 'yes' and not records:
            self.payment_state = 'unpaid'
            print(self.payment_state)
        else:
            self.payment_state = 'not_app'
            print(self.payment_state)

    @api.onchange("branch_id")
    def _onchange_analytic_tag(self):
        for rec in self:
            record = self.env['account.analytic.tag'].search([('branch_id', '=', rec.branch_id.id)])
            rec.order_line.branch_id = rec.branch_id.id
            print(record)
            rec.order_line.analytic_tag_ids = record

    def write(self, values):
        res = super(PurchaseOrderInherit, self).write(values)
        tags = self.env['account.analytic.tag'].search([('branch_id', '=', self.branch_id.id)])
        for line in self.order_line:
            line.analytic_tag_ids = tags.ids
