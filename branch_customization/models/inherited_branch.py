from odoo import models, fields, api


class InheritedBranch(models.Model):
    _inherit = 'res.branch'

    analytical_tag_id = fields.Many2one('account.analytic.tag', string="Analytic Tag")

    @api.model
    def create(self, vals):
        res = super(InheritedBranch, self).create(vals)
        result = self.env['account.analytic.tag'].create(
            {'name': res['name'],
             'branch_id': res.id,
             })
        res.analytical_tag_id = result.id
        return res

