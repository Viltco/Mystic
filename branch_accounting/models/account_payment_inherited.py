from odoo import models, fields, api
from odoo.exceptions import UserError


class PaymentInherited(models.Model):
    _inherit = 'account.payment'

    # is_multi_branch = fields.Boolean(string='Multi Branch Payment')
    is_multi_branch = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Multi Branch Payment')
    branch_entries_id = fields.One2many('res.branch.entries', 'payment_id', string='Branch Entries')
    # move_id2 = fields.Many2one('account.move', string='Multi Branch Entry')
    move_id3 = fields.Many2one('account.move', string='Branch Entry')

    @api.constrains('is_multi_branch')
    def _check_is_multi_branch(self):
        for rec in self:
            if rec.is_multi_branch == 'yes':
                if not rec.branch_entries_id:
                    raise UserError(f"Please Enter At-Lease one Branch Entry or uncheck Multi Branch")

    def action_create_jv(self):
        lines = []
        reference = ''
        for record in self:
            if record.is_multi_branch == 'yes':
                for line in record.payment_invoice_ids:
                    tags = self.env['account.analytic.tag'].search([('branch_id', '=', line.branch_id.id)])
                    debit_line = (0, 0, {
                        'name': 'Payment',
                        'debit': line.reconcile_amount,
                        'credit': 0.0,
                        'partner_id': record.partner_id.id,
                        'account_id': record.destination_account_id.id,
                        'branch_id': line.branch_id.id,
                        'analytic_tag_ids': tags
                    })
                    lines.append(debit_line)
                    credit_line = (0, 0, {
                        'name': 'Advance Payment',
                        'debit': 0.0,
                        'partner_id': record.partner_id.id,
                        'credit': line.reconcile_amount,
                        'account_id': record.destination_account_id.id,
                        'branch_id': line.branch_id.id,
                        'analytic_tag_ids': tags
                    })
                    lines.append(credit_line)
                    reference += line.invoice_id.name
                    reference += ' '
                print(reference)
                move_dict = {
                    'payment_id': record.id,
                    'ref': reference, 'branch_id': record.branch_id.id, 'move_type': 'entry',
                    'journal_id': record.journal_id.id, 'partner_id': record.partner_id.id,
                    'date': record.date, 'state': 'draft', 'line_ids': lines}
                move = self.env['account.move'].create(move_dict)
                record.move_id2 = move.id
                print('created')
            else:
                raise UserError('Please Marked Multi Branch')

    def action_branch_entries_jv(self):
        lines = []
        for record in self:
            if record.is_multi_branch:
                for line in record.branch_entries_id:
                    # tags = self.env['account.analytic.tag'].search([('branch_id', '=', line.receiving_branch_id.id)])
                    debit_line = (0, 0, {
                        'name': '',
                        'debit': line.amount,
                        'credit': 0.0,
                        'partner_id': line.partner_id_to.id,
                        'account_id': line.receiving_branch_id.account_rec_id.id,
                        'branch_id': line.receiving_branch_id.id,
                        'analytic_tag_ids': line.receiving_branch_id.analytical_tag_id.ids
                    })
                    lines.append(debit_line)
                    # tags = self.env['account.analytic.tag'].search([('branch_id', '=', line.payable_branch_id.id)])
                    credit_line = (0, 0, {
                        'name': '',
                        'debit': 0.0,
                        'partner_id': line.partner_id_from.id,
                        'credit': line.amount,
                        'account_id': line.payable_branch_id.account_pay_id.id,
                        'branch_id': line.payable_branch_id.id,
                        'analytic_tag_ids': line.payable_branch_id.analytical_tag_id.ids
                    })
                    lines.append(credit_line)
                move_dict = {
                    'payment_id': record.id,
                    'ref': record.name, 'branch_id': record.branch_id.id, 'move_type': 'entry',
                    'journal_id': record.journal_id.id, 'partner_id': record.partner_id.id,
                    'date': record.date,
                    'state': 'draft', 'line_ids': lines}
                print(move_dict)
                move = self.env['account.move'].create(move_dict)
                record.move_id3 = move.id
            else:
                raise UserError('Please Marked Multi Branch')
