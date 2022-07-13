# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError,RedirectWarning


class ResBranchInh(models.Model):
    _inherit = 'res.branch'

    fiscal_position_id = fields.Many2one('account.fiscal.position')


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    @api.onchange('branch_id')
    def onchange_branch(self):
        self.fiscal_position_id = self.branch_id.fiscal_position_id.id

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self = self.with_company(self.journal_id.company_id)

        warning = {}
        if self.partner_id:
            rec_account = self.partner_id.property_account_receivable_id
            pay_account = self.partner_id.property_account_payable_id
            if not rec_account and not pay_account:
                action = self.env.ref('account.action_account_config')
                msg = _(
                    'Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
                raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))
            p = self.partner_id
            if p.invoice_warn == 'no-message' and p.parent_id:
                p = p.parent_id
            if p.invoice_warn and p.invoice_warn != 'no-message':
                # Block if partner only has warning but parent company is blocked
                if p.invoice_warn != 'block' and p.parent_id and p.parent_id.invoice_warn == 'block':
                    p = p.parent_id
                warning = {
                    'title': _("Warning for %s", p.name),
                    'message': p.invoice_warn_msg
                }
                if p.invoice_warn == 'block':
                    self.partner_id = False
                    return {'warning': warning}

        if self.is_sale_document(include_receipts=True) and self.partner_id:
            self.invoice_payment_term_id = self.partner_id.property_payment_term_id or self.invoice_payment_term_id
            new_term_account = self.partner_id.commercial_partner_id.property_account_receivable_id
        elif self.is_purchase_document(include_receipts=True) and self.partner_id:
            self.invoice_payment_term_id = self.partner_id.property_supplier_payment_term_id or self.invoice_payment_term_id
            new_term_account = self.partner_id.commercial_partner_id.property_account_payable_id
        else:
            new_term_account = None

        for line in self.line_ids:
            line.partner_id = self.partner_id.commercial_partner_id

            if new_term_account and line.account_id.user_type_id.type in ('receivable', 'payable'):
                line.account_id = new_term_account

        self._compute_bank_partner_id()
        self.partner_bank_id = self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]

        # Find the new fiscal position.
        delivery_partner_id = self._get_invoice_delivery_partner_id()
        # self.fiscal_position_id = self.env['account.fiscal.position'].get_fiscal_position(
        #     self.partner_id.id, delivery_id=delivery_partner_id)
        self._recompute_dynamic_lines()
        if warning:
            return {'warning': warning}


class AccountAccountInh(models.Model):
    _inherit = 'account.account'

    code = fields.Char(size=64, required=False, index=True)

    @api.model
    def create(self, vals):
        accounts = self.env['account.account'].search([('group_id', '=', vals['group_id'])], order="id desc")
        group = self.env['account.group'].search([('id', '=', vals['group_id'])])
        if not accounts:
            code = group.code_prefix_start
        elif accounts:
            code = int(accounts[0].code) + 1
            if len(str(code)) < len(group.code_prefix_start):
                i = len(group.code_prefix_start) - len(str(code))
                for j in range(0, i):
                    code = '0' + str(code)
        if int(code) > int(group.code_prefix_end):
            raise UserError('Limit is Exceeded')
        vals['code'] = code
        result = super(AccountAccountInh, self).create(vals)
        return result

    def action_assign_code(self):
        groups = self.env['account.account'].search([]).mapped('group_id')
        for g in groups:
            k = ''
            accounts = self.env['account.account'].search([('group_id', '=', g.id)])
            group = self.env['account.group'].search([('id', '=', g.id)])
            h = 0
            for account in accounts:
                if h == 0:
                    code = group.code_prefix_start
                    h = h + 1
                    k = int(code)
                    account.code = code
                else:
                    code = int(k) + 1
                    if len(str(code)) < len(group.code_prefix_start):
                        i = len(group.code_prefix_start) - len(str(code))
                        for j in range(0, i):
                            code = '0' + str(code)
                    h = h + 1
                    k = int(code)
                    account.code = code
