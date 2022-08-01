from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BranchInherited(models.Model):
    _inherit = 'res.branch'

    account_rec_id = fields.Many2one('account.account', string='Receivable Account', store=True, readonly=False,
                                     domain="[('user_type_id.type', '=', 'receivable')]")
    account_pay_id = fields.Many2one('account.account', string='Payable Account', store=True, readonly=False,
                                     domain="[('user_type_id.type', '=', 'payable')]")
    inter_branch_journal = fields.Many2one('account.journal', string='Inter Branch')