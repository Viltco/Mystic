# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'
    # purchase_id = fields.Many2one('purchase.order')
    advance_status = fields.Selection(selection=[
        ('not_app', 'N/A'),
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid')
    ], string='Advance Status')
    paid_amount = fields.Float(string='Paid Amount')
    advance_journal = fields.Many2one('account.journal', string='Account Journal')
    hide_aj = fields.Boolean(default=False)
    advance_account = fields.Many2one(
        comodel_name='account.account',
        string='Advance Account',
        store=True, readonly=False,
        domain="[('user_type_id.type', 'in', ('receivable', 'payable')), ('company_id', '=', company_id)]")

    #
    # @api.depends('purchase_vendor_bill_id')
    # def _compute_advance_status(self):
    #     for rec in self:
    #         rec.advance_status = rec.purchase_vendor_bill_id
    #         print(rec.advance_status)

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        ''' Load from either an old purchase order, either an old vendor bill.

        When setting a 'purchase.bill.union' in 'purchase_vendor_bill_id':
        * If it's a vendor bill, 'invoice_vendor_bill_id' is set and the loading is done by '_onchange_invoice_vendor_bill'.
        * If it's a purchase order, 'purchase_id' is set and this method will load lines.

        /!\ All this not-stored fields must be empty at the end of this function.
        '''
        if self.purchase_vendor_bill_id.vendor_bill_id:
            self.invoice_vendor_bill_id = self.purchase_vendor_bill_id.vendor_bill_id
            self._onchange_invoice_vendor_bill()
        elif self.purchase_vendor_bill_id.purchase_order_id:
            self.purchase_id = self.purchase_vendor_bill_id.purchase_order_id
        self.purchase_vendor_bill_id = False

        if not self.purchase_id:
            return

        # Copy data from PO
        invoice_vals = self.purchase_id.with_company(self.purchase_id.company_id)._prepare_invoice()
        invoice_vals['currency_id'] = self.line_ids and self.currency_id or invoice_vals.get('currency_id')
        del invoice_vals['ref']
        self.update(invoice_vals)

        # Copy purchase lines.
        po_lines = self.purchase_id.order_line - self.line_ids.mapped('purchase_line_id')

        # Custom
        self.advance_status = self.purchase_id.payment_state
        paid_records = self.env['account.payment'].search(
            ['&', ('state', '=', 'posted'), ('is_advance_pay', '=', True),
             ('purchase_order_id', '=', self.purchase_id.id)])
        if self.purchase_id.payment_state == 'paid':
            self.paid_amount = 0.00
        else:
            total_payment = 0
            for rec in paid_records:
                total_payment += rec.amount
            self.paid_amount = self.purchase_id.advance_amount - total_payment
        if self.purchase_id.is_advance_payment == 'yes':
            self.hide_aj = True
        else:
            self.hide_aj = False
            self.paid_amount = 0.00
        new_lines = self.env['account.move.line']
        for line in po_lines.filtered(lambda l: not l.display_type):
            new_line = new_lines.new(line._prepare_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()

        # Compute invoice_origin.
        origins = set(self.line_ids.mapped('purchase_line_id.order_id.name'))
        self.invoice_origin = ','.join(list(origins))

        # Compute ref.
        refs = self._get_invoice_reference()
        self.ref = ', '.join(refs)

        # Compute payment_reference.
        if len(refs) == 1:
            self.payment_reference = refs[0]

        self.purchase_id = False
        self._onchange_currency()
        self.partner_bank_id = self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]

    def action_create_jv(self):
        lines = []
        debit_sum = 0.0
        credit_sum = 0.0
        for record in self:
            move_dict = {
                'ref': record.name,
                'branch_id': record.branch_id.id,
                'move_type': 'entry',
                'journal_id': record.advance_journal.id,
                'partner_id': record.partner_id.id,
                'date': record.date,
                'state': 'draft',
            }
            debit_line = (0, 0, {
                'name': 'Advance Payment',
                'debit': record.paid_amount,
                'credit': 0.0,
                'partner_id': record.partner_id.id,
                'account_id': record.partner_id.property_account_payable_id.id,
            })
            lines.append(debit_line)
            debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
            credit_line = (0, 0, {
                'name': 'Advance Payment',
                'debit': 0.0,
                'partner_id': record.partner_id.id,
                'credit': record.paid_amount,
                'account_id': record.advance_account.id,
            })
            lines.append(credit_line)
            credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            move_dict['line_ids'] = lines
            move = self.env['account.move'].create(move_dict)
            print('JV Created')

    def draft_validation(self, active_model, records):
        total = 0
        if records:
            for rec in records:
                total += rec.line_ids[0].debit

        po_rec = self.env['purchase.order'].search(
            ['&', ('partner_id', '=', active_model.partner_id.id), ('branch_id', '=', active_model.branch_id.id),
             ('payment_state', '=', active_model.advance_status)])
        print(po_rec)
        po_rec.payment_state = 'paid'
        active_model.advance_status = 'paid'
        total_plus = total + self.line_ids[0].debit
        print(total)
        print(self.move_type)
        if total_plus > active_model.paid_amount:
            raise UserError('Advance has already been paid')


    def action_post(self):
        active_model = self.env['account.move'].browse(self.env.context.get('active_id'))
        if self.move_type == 'entry' and self.line_ids[-1].account_id.id == active_model.advance_account.id:
            print('yes')
            records = self.env['account.move'].search(
                ['&', ('ref', '=', active_model.name), ('state', '=', 'posted')])
            self.draft_validation(active_model, records)
        self._post(soft=False)
        return False
        # self.write({
        #     'state': 'approve'
        # })

    def get_bills_jvs(self):
        return {
            'name': _('Journal Entries'),
            'domain': [('ref', '=', self.name)],
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
