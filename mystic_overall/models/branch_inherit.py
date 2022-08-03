from odoo import api, models, fields


class BranchSequence(models.Model):
    _inherit = "ir.sequence"

    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True)


class ResBranchCode(models.Model):
    _inherit = "res.branch"

    code = fields.Char()

    journal_id = fields.Many2one('account.journal', string="Journal")
    category_id = fields.Many2one('res.partner.category', string="Tags")

    @api.model
    def create(self, vals):
        res = super(ResBranchCode, self).create(vals)
        result = self.env['account.journal'].create(
            {'name': res['name'] + '-' + 'Miscellaneous',
             'branch_id': res.id,
             'type': 'general',
             'code': res['code'],
             })
        res.journal_id = result.id
        tag = self.env['res.partner.category'].create(
            {'name': res['name'],
             })
        res.category_id = tag.id
        return res
