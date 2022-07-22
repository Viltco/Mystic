# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from datetime import datetime
from datetime import date


class LeaseBill(models.Model):
    _name = 'lease.bill'
    _description = 'Lease Bill'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id
        return branch_id

    branch_id = fields.Many2one('res.branch', default=_default_branch_id)
    name = fields.Char(string='Name')

    bill_id = fields.Many2one('account.move', string='Bill Reference',
                              domain=lambda self: [("move_type", "=", 'in_invoice')])

    amount_bill = fields.Float(string='Outstanding Amount')

    pre_lease_id = fields.Many2one('lease.bill', string='Previous Lease')

    kibor = fields.Float(string='KIBOR %')
    interest_rate = fields.Float(string='Interest Rate %')
    applicable_for = fields.Integer(string='Installment Months')

    installment_total = fields.Integer(string='Total Installments')
    installment_done = fields.Integer(string='Done Installments')
    installment_remain = fields.Integer(string='Remaining Installments', compute='_compute_installment_remain')
    interest_date_due = fields.Date(string='Interest Due Date')

    # lease_long_term_id = fields.Many2one('account.account', string='Lease Account Long Term')
    # lease_current_id = fields.Many2one('account.account', string='Lease Account Current')
    # interest_expense_id = fields.Many2one('account.account', string='Interest Expense Account')
    interest_expense_id = fields.Many2one('product.product', string='Interest Expense',
                                          domain="[('type', '=', 'service')]")

    lease_journal_id = fields.Many2one('account.journal', string='Journal')
    destination_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Destination Account',
        store=True, readonly=False,
        domain="[('user_type_id.type', 'in', ('receivable', 'payable'))]")
    date = fields.Date(string='Date')
    date_bill = fields.Date(string='Bill Date')
    date_prin_due = fields.Date(string='Principal Due Date')
    partner_id = fields.Many2one('res.partner', string='Vendor')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
    ], string='Status', default='draft')

    lease_bill_lines = fields.One2many('lease.bill.line', 'lease_bill_id')

    is_installment = fields.Boolean(string='Is Installment')
    is_draft_entry = fields.Boolean(string='Is Draft Entry', default=True)

    move_count = fields.Integer(string="Move Count", compute='_compute_total_moves', tracking=True)

    # Other Info Page

    pre_lease_bill_id = fields.Many2one('lease.bill', string='Previous Lease Bill Link')

    @api.model
    def create(self, vals):
        sequence = self.env.ref('lease_bill.lease_bill_sequence')
        journal_record = self.env['account.journal'].browse(vals['lease_journal_id'])
        # journal_code = str(journal_record.code)
        current_year = str(date.today().year)
        current_month = str(date.today().month)
        pos_seq = sequence.next_by_id()
        pre_seq = ('Lease' + '/' + current_year + '/' + current_month)
        vals['name'] = (pre_seq + str(pos_seq))
        rec = super(LeaseBill, self).create(vals)
        return rec

    def action_draft(self):
        self.write({
            'state': 'draft'
        })

    def action_update_installments(self):
        moves = self.env['account.move'].search([('lease_bill_id', '=', self.id)]).mapped('id')
        moves_line = self.env['account.move.line'].search([('move_id', 'in', moves)]).unlink()
        mv = self.env['account.move'].search([('lease_bill_id', '=', self.id)]).unlink()
        for line in self.lease_bill_lines:
            line.unlink()
        self.write({
            'state': 'draft'
        })
        self.is_installment = False

    def action_post(self):
        self.write({
            'state': 'posted',
            'is_draft_entry': False
        })

    def unlink(self):
        for record in self:
            if record.state == 'posted':
                raise Warning(_('You can not delete Lease Bill which is not in draft state.'))
            else:
                return super(LeaseBill, self).unlink()

    @api.onchange('bill_id')
    def _onchange_bill_id(self):
        print()
        for record in self:
            print(record.bill_id.branch_id.name)
            record.amount_bill = record.bill_id.amount_residual
            record.date_bill = record.bill_id.invoice_date
            record.partner_id = record.bill_id.partner_id.id
            record.branch_id = record.bill_id.branch_id.id

    @api.depends('installment_total', 'installment_done')
    def _compute_installment_remain(self):
        for record in self:
            if record.installment_total or record.installment_done:
                record.installment_remain = record.installment_total - record.installment_done
            else:
                record.installment_remain = 0

    def action_create_installment(self):
        annum_perc = (self.kibor + self.interest_rate) / 100
        annum_amnt = self.amount_bill * annum_perc
        mont_amnt = annum_amnt / 12
        return {
            'type': 'ir.actions.act_window',
            'name': 'Schedule Installments',
            'view_id': self.env.ref('lease_bill.view_lease_wizard_form', False).id,
            'context': {'default_amount': self.amount_bill,
                        'default_installment_date_due': self.interest_date_due,
                        'default_prin_date_due': self.date_prin_due,
                        'default_intr_part': mont_amnt,
                        'default_interest_months': self.applicable_for,
                        'branch_id': self.branch_id.id},
            'target': 'new',
            'res_model': 'lease.wizard',
            'view_mode': 'form',
        }

    # # Journal Entry Creation
    # Bill Creation
    def create_draft_entry(self):
        line_vals = []
        for line in self.lease_bill_lines:
            line_vals.append((0, 0, {
                'product_id': self.interest_expense_id.id,
                'name': self.interest_expense_id.name,
                'price_unit': line.int_part,
                'quantity': 1.0,
                'account_id': self.interest_expense_id.property_account_expense_id.id
            }))

            bill = {
                'lease_bill_id': self.id,
                'invoice_line_ids': line_vals,
                'partner_id': self.partner_id.id,
                'branch_id': self.branch_id.id,
                'invoice_date': line.date_due,
                'date': line.date_due,
                'state': 'draft',
                # 'hide_jv_link': True,
                'journal_id': self.lease_journal_id.id,
                'move_type': 'in_invoice'
            }
            record = self.env['account.move'].create(bill)
            print(record)
            line.move_id = record.id
            line.move_id.state = record.state
            line.branch_id = record.branch_id.id
            line_vals = []
        self.is_draft_entry = True

    def action_move_view(self):
        return {
            'name': _('Journal Entries'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('lease_bill_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }

    def _compute_total_moves(self):
        records = self.env['account.move'].search_count([('lease_bill_id', '=', self.id)])
        self.move_count = records


class LeaseBillLines(models.Model):
    _name = 'lease.bill.line'
    _description = 'Lease Bill Line'
    _rec_name = 'partner_id'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Confirm'),
        ('cancel', 'Cancel')
    ])
    lease_bill_id = fields.Many2one('lease.bill', string='Lease Bill')
    partner_id = fields.Many2one('res.partner', string='Vendor', related='lease_bill_id.partner_id')
    bill_id = fields.Many2one('account.move', string='Bill Reference',
                              domain=lambda self: [("move_type", "=", 'in_invoice')], related='lease_bill_id.bill_id')
    move_id = fields.Many2one('account.move', string='Installment Bills',
                              domain=lambda self: [("move_type", "=", 'in_invoice')])
    payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy')],
        string="Payment Status", store=True, readonly=True, copy=False, related='move_id.payment_state')
    # date_account = fields.Date(string='Date')
    date_due = fields.Date(string='Due Date')
    prin_part = fields.Float(string='Principal Part')
    int_part = fields.Float(string='Interest Part')
    due_total = fields.Float(string='Total Due')
    prin_balance = fields.Float(string='Balance Principal')
    branch_id = fields.Many2one('res.branch')

    def action_register_payment(self):
        total_interest = 0
        total_principle = 0
        partner_counter = self[0].partner_id.id
        branch_counter = self[0].branch_id.id
        lines_list = []
        for rec in self:
            if partner_counter != rec.partner_id.id:
                raise UserError('Please Select the same Partner')
            elif branch_counter != rec.branch_id.id:
                raise UserError('Please Select the same Branch Bills')
            elif rec.move_id.state != 'posted':
                raise UserError("Draft Bill Can't be Paid. Please post the bill first")
            else:
                total_interest += rec.int_part
                lines_list.append(rec.move_id.name)
                if rec.prin_part != 0.0:
                    total_principle += rec.prin_part
        total = total_interest + total_principle
        return {
            'type': 'ir.actions.act_window',
            'name': 'Apply Lease Payments',
            'view_id': self.env.ref('lease_bill.view_lease_payment_wizard_form', False).id,
            'context': {
                'default_amount': total,
                'default_partner_id': self.partner_id.id,
                # 'default_ref': self.bill_id.name + ' ' + ' '.join(lines_list) ,
                'default_ref': ' '.join(lines_list) ,
                'default_destination_account_id': self.lease_bill_id.destination_account_id.id,
                'default_branch_id': self.branch_id.id,
                'default_lines_list': lines_list,
            },
            'target': 'new',
            'res_model': 'lease.payment.wizard',
            'view_mode': 'form',
        }

    def action_post_bill(self):
        for rec in self:
            rec.state = 'posted'
            rec.move_id.state = 'posted'

    def action_draft_bill(self):
        for rec in self:
            rec.state = 'draft'
            rec.move_id.state = 'draft'

    def action_cancel_bill(self):
        for rec in self:
            rec.state = 'cancel'
            rec.move_id.state = 'cancel'
