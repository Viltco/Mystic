# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EmpConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    account_id = fields.Many2one('account.account', string='Advance Adjustment Account',
                                 domain="[('user_type_id.type', 'in', ('receivable', 'payable')), ('company_id', '=', company_id)]",
                                 config_parameter='advance_payment_purchase.account_id')
