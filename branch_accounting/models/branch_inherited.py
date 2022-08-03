from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BranchInherited(models.Model):
    _inherit = 'res.branch'

    # account_rec_id = fields.Many2one('account.account', string='Receivable Account', store=True, readonly=False,
    #                                  domain="[('user_type_id.type', '=', 'receivable')]")
    # account_pay_id = fields.Many2one('account.account', string='Payable Account', store=True, readonly=False,
    #                                  domain="[('user_type_id.type', '=', 'payable')]")
    partner_id = fields.Many2one('res.partner', string='Vendor')

    @api.model
    def create(self, vals):
        res = super(BranchInherited, self).create(vals)
        # Create Chart of Account for Receivable
        receivable = self.env['account.account'].create(
            {'name': 'Receivable From ' + res['name'],
             'user_type_id': self.env.ref('account.data_account_type_receivable').id,
             'group_id': self.env['account.group'].search(
                 [('id', '=',
                   self.env['ir.config_parameter'].get_param('branch_accounting.branch_receivable_group'))]).id,
             'reconcile': True,
             })
        # Create Chart of Account for Payable
        payable = self.env['account.account'].create(
            {'name': 'Payable To ' + res['name'],
             'user_type_id': self.env.ref('account.data_account_type_payable').id,
             'group_id': self.env['account.group'].search(
                 [('id', '=',
                   self.env['ir.config_parameter'].get_param('branch_accounting.branch_payable_group'))]).id,
             'reconcile': True,
             })

        # Create Vendor
        vendor = self.env['res.partner'].create({
            'company_type': 'company',
            'name': res['name'],
            'partner_type': 'is_vendor',
            'branch_id': res.id,
            'property_account_receivable_id': receivable.id,
            'property_account_payable_id': payable.id
        })
        print(res.id)
        res.partner_id = vendor.id
        print(res.id)
        return res
