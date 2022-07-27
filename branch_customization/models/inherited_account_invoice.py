# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id
        print('-------------------------------------------')
        return branch_id

    branch_id = fields.Many2one('res.branch', default=_default_branch_id, required=True)
    allow_multi_branch = fields.Boolean(related='journal_id.multi_branch_only')
    @api.onchange("branch_id")
    def _onchange_analytic_tag(self):
        for rec in self:
            records = self.env['account.journal'].search(
                ['&',('multi_branch_only', '=', False),('name', '=', rec.journal_id.name)])
            if records:
                tags = self.env['account.analytic.tag'].search([('branch_id', '=', rec.branch_id.id)])
                rec.line_ids.branch_id = rec.branch_id.id
                rec.line_ids.analytic_tag_ids = tags

    @api.model
    def create(self, values):
        res = super(AccountMove, self).create(values)
        records = self.env['account.journal'].search(
            ['&', ('multi_branch_only', '=', False), ('name', '=', self.journal_id.name)])
        if records:
            for invoice in res.invoice_line_ids:
                invoice.branch_id = res.branch_id
                tags = self.env['account.analytic.tag'].search([('branch_id.id', '=', res.branch_id.id)])
                invoice.analytic_tag_ids = tags

            for line1 in res.line_ids:
                line1.branch_id = res.branch_id
                tags = self.env['account.analytic.tag'].search([('branch_id.id', '=', res.branch_id.id)])
                line1.analytic_tag_ids = tags
        # else:
        #     for invoice in res.invoice_line_ids:
        #         if not invoice.branch_id:
        #             invoice.branch_id = res.branch_id
        #             tags = self.env['account.analytic.tag'].search([('branch_id.id', '=', res.branch_id.id)])
        #             invoice.analytic_tag_ids = tags
        #         else:
        #             tags = self.env['account.analytic.tag'].search([('branch_id.id', '=', invoice.branch_id.id)])
        #             invoice.analytic_tag_ids = tags
        #
        #     for line1 in res.line_ids:
        #         if not line1.branch_id:
        #             line1.branch_id = res.branch_id
        #             tags = self.env['account.analytic.tag'].search([('branch_id.id', '=', res.branch_id.id)])
        #             line1.analytic_tag_ids = tags
        #         else:
        #             tags = self.env['account.analytic.tag'].search([('branch_id.id', '=', line1.branch_id.id)])
        #             line1.analytic_tag_ids = tags

        return res

    def write(self, values):
        res = super(AccountMove, self).write(values)
        records = self.env['account.journal'].search(
            ['&', ('multi_branch_only', '=', False), ('name', '=', self.journal_id.name)])
        if records:
            tags = self.env['account.analytic.tag'].search([('branch_id', '=', self.branch_id.id)])
            for line in self.invoice_line_ids:
                line.branch_id = self.branch_id
                line.analytic_tag_ids = tags.ids
            for line1 in self.line_ids:
                line1.branch_id = self.branch_id
                line1.analytic_tag_ids = tags.ids
        # else:
        #
        #     for line in self.invoice_line_ids:
        #         if not line.branch_id:
        #             tags = self.env['account.analytic.tag'].search([('branch_id', '=', self.branch_id.id)])
        #             line.branch_id = self.branch_id
        #             line.analytic_tag_ids = tags.ids
        #         else:
        #             tags = self.env['account.analytic.tag'].search([('branch_id', '=', line.branch_id.id)])
        #             line.analytic_tag_ids = tags.ids
        #     for line1 in self.line_ids:
        #         if not line1.branch_id:
        #             tags = self.env['account.analytic.tag'].search([('branch_id', '=', self.branch_id.id)])
        #             line1.branch_id = self.branch_id
        #             line1.analytic_tag_ids = tags.ids
        #         else:
        #             tags = self.env['account.analytic.tag'].search([('branch_id', '=', line1.branch_id.id)])
        #             line1.analytic_tag_ids = tags.ids
        return res

    def action_register_payment(self):

        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
                'default_branch_id': self.branch_id.id,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _default_branch_id(self):
        branch_id = self.env['res.users'].browse(self._uid).branch_id.id
        return branch_id

    branch_id = fields.Many2one('res.branch')
    allow_multi_branch = fields.Boolean(related='move_id.allow_multi_branch')

    @api.onchange('branch_id')
    def _onchange_branch(self):
        for rec in self:
            if rec.branch_id:
                tags = self.env['account.analytic.tag'].search([('branch_id', '=', rec.branch_id.id)])
                rec.analytic_tag_ids = tags
            else:
                rec.analytic_tag_ids = False


class AccountAccountInherited(models.Model):
    _inherit = 'account.journal'
    multi_branch_only = fields.Boolean(string='Allow Multi Branch Only')
