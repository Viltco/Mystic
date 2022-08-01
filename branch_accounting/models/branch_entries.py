from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BranchEntries(models.Model):
    _name = 'res.branch.entries'

    payment_id = fields.Many2one('account.payment')
    receiving_branch_id = fields.Many2one('res.branch', string='Receiving Branch')
    partner_id_to = fields.Many2one('res.partner', string='Partner (To)')
    payable_branch_id = fields.Many2one('res.branch', string='Payable Branch')
    partner_id_from = fields.Many2one('res.partner', string='Partner (From)')
    amount = fields.Float('Amount')
