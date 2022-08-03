from odoo import models, fields, api


class ConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    inter_branch_journal = fields.Many2onejournal_id = fields.Many2one('account.journal', string='Inter Branch Journal',
                                           config_parameter='branch_accounting.inter_branch_journal')
    branch_payable_group = fields.Many2one('account.group', string='Branch Payable Group',
                                           config_parameter='branch_accounting.branch_payable_group')
    branch_receivable_group = fields.Many2one('account.group', string='Branch Receivable Group',
                                              config_parameter='branch_accounting.branch_receivable_group')
