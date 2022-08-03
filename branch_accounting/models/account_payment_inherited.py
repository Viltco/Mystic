from odoo import models, fields, api
from odoo.exceptions import UserError


class PaymentInherited(models.Model):
    _inherit = 'account.payment'

    is_multi_branch = fields.Selection([('yes', 'YES'), ('no', 'NO')], string='Multi Branch Payment')
    branch_entries_id = fields.One2many('res.branch.entries', 'payment_id', string='Branch Entries')
    move_id3 = fields.Many2one('account.move', string='Branch Entry')

    @api.constrains('is_multi_branch')
    def _check_is_multi_branch(self):
        for rec in self:
            if rec.is_multi_branch == 'yes':
                if not rec.branch_entries_id:
                    raise UserError(f"Please Enter At-Lease one Branch Entry or uncheck Multi Branch")

    def action_branch_entries_jv(self):
        lines = []
        for record in self:
            if record.is_multi_branch:
                for line in record.branch_entries_id:
                    debit_line = (0, 0, {
                        'name': '',
                        'debit': line.amount,
                        'credit': 0.0,
                        'partner_id': line.partner_id_to.id,
                        'account_id': line.partner_id_to.property_account_receivable_id.id,
                        'branch_id': line.receiving_branch_id.id,
                        'analytic_tag_ids': line.receiving_branch_id.analytical_tag_id.ids
                    })
                    lines.append(debit_line)
                    credit_line = (0, 0, {
                        'name': '',
                        'debit': 0.0,
                        'partner_id': line.partner_id_from.id,
                        'credit': line.amount,
                        'account_id': line.partner_id_from.property_account_payable_id.id,
                        'branch_id': line.payable_branch_id.id,
                        'analytic_tag_ids': line.payable_branch_id.analytical_tag_id.ids
                    })
                    lines.append(credit_line)
                move_dict = {
                    'payment_id': record.id,
                    'ref': record.name, 'branch_id': record.branch_id.id, 'move_type': 'entry',
                    'journal_id': int(self.env['ir.config_parameter'].get_param('branch_accounting.inter_branch_journal')),
                    'date': record.date,
                    'state': 'draft', 'line_ids': lines}
                move = self.env['account.move'].create(move_dict)
                record.move_id3 = move.id
            else:
                raise UserError('Please Marked Multi Branch')
