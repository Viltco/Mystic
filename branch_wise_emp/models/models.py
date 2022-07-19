from odoo import api, models, fields


class InheritedHrEmployee(models.Model):
    _inherit = 'hr.contract'

    branch_id = fields.Many2one('res.branch', related='employee_id.branch_id', readonly=True)
    analytic_tag_id = fields.Many2many('account.analytic.tag', string='Analytic Tag',
                                       domain="[('branch_id', '=', branch_id)]", readonly=True,
                                       related='employee_id.analytic_tag_id')


class InheritedHrEmployee(models.Model):
    _inherit = 'hr.employee'

    branch_id = fields.Many2one('res.branch', default=lambda r: r.env.user.branch_id.id)
    analytic_tag_id = fields.Many2many('account.analytic.tag', string='Analytic Tag',
                                       domain="[('branch_id', '=', branch_id)]", readonly=True)

    @api.onchange('branch_id')
    def set_contract_branch(self):
        record = self.env['account.analytic.tag'].search([('branch_id', '=', self.branch_id.id)])
        print(record.name)
        self.analytic_tag_id = record
