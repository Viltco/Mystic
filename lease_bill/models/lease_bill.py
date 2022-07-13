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

    name = fields.Char(string='Name')

    bill_id = fields.Many2one('account.move', string='Bill Reference',
                                  domain=lambda self: [("move_type", "=", 'in_invoice')])

    amount_bill = fields.Float(string='Outstanding Amount')

    branch_id = fields.Many2one('res.branch', string='Branch')
    pre_lease_id = fields.Many2one('lease.bill', string='Previous Lease')

    kibor = fields.Float(string='KIBOR %')
    interest_rate = fields.Float(string='Interest Rate %')
    applicable_for = fields.Integer(string='Installment Months')

    installment_total = fields.Integer(string='Total Installments')
    installment_done = fields.Integer(string='Done Installments')
    installment_remain = fields.Integer(string='Remaining Installments', compute='_compute_installment_remain')
    interest_date_due = fields.Date(string='Interest Due Date')

    lease_long_term_id = fields.Many2one('account.account', string='Lease Account Long Term')
    lease_current_id = fields.Many2one('account.account', string='Lease Account Current')
    interest_expense_id = fields.Many2one('account.account', string='Interest Expense Account')

    lease_journal_id = fields.Many2one('account.journal', string='Journal')

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

    move_count = fields.Integer(string="Move Count", compute='_compute_total_moves', tracking=True)

    # Other Info Page

    pre_lease_bill_id = fields.Many2one('lease.bill', string='Previous Lease Bill Link')

    @api.model
    def create(self, vals):
        sequence = self.env.ref('lease_bill.lease_bill_sequence')
        journal_record = self.env['account.journal'].browse(vals['lease_journal_id'])
        journal_code = str(journal_record.code)
        current_year = str(date.today().year)
        current_month = str(date.today().month)
        pos_seq = sequence.next_by_id()
        pre_seq = (journal_code + '/' + current_year + '/' + current_month)
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
            'state': 'posted'
        })

    def unlink(self):
        for record in self:
            if record.state == 'posted':
                raise Warning(_('You can not delete Lease Bill which is not in draft state.'))
            else:
                return super(LeaseBill, self).unlink()

    @api.onchange('bill_id')
    def _onchange_bill_id(self):
        for record in self:
            record.amount_bill = record.bill_id.amount_residual
            record.date_bill = record.bill_id.invoice_date

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
                        'default_interest_months': self.applicable_for},
            'target': 'new',
            'res_model': 'lease.wizard',
            'view_mode': 'form',
        }

    # Journal Entry Creation

    def create_draft_entry(self):
        line_ids = []
        debit_sum = 0.0
        new_debit_sum = 0.0
        credit_sum = 0.0
        for line in self.lease_bill_lines:
            move_dict = {
                'ref': self.name,
                'journal_id': self.lease_journal_id.id,
                'lease_bill_id': self.id,
                'partner_id': self.partner_id.id,
                'date': datetime.today(),
                'state': 'draft',
            }
            debit_line = (0, 0, {
                'name': 'Lease Installment',
                'debit': abs(line.int_part),
                'credit': 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.interest_expense_id.id,
            })
            line_ids.append(debit_line)
            debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
            new_debit_line = (0, 0, {
                'name': 'Lease Installment',
                'debit': abs(line.prin_part),
                'credit': 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.lease_long_term_id.id,
            })
            line_ids.append(new_debit_line)
            new_debit_sum += new_debit_line[2]['debit'] - new_debit_line[2]['credit']
            credit_line = (0, 0, {
                'name': 'Lease Installment',
                'debit': 0.0,
                'partner_id': self.partner_id.id,
                'credit': abs(line.prin_part + line.int_part),
                'account_id': self.lease_current_id.id,
            })
            line_ids.append(credit_line)
            credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            line_ids = []

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

    lease_bill_id = fields.Many2one('lease.bill')

    date_account = fields.Date(string='Accounting Date')
    date_due = fields.Date(string='Due Date')
    prin_part = fields.Float(string='Principal Part')
    int_part = fields.Float(string='Interest Part')
    due_total = fields.Float(string='Total Due')
    prin_balance = fields.Float(string='Balance Principal')
