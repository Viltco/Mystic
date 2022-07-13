from odoo import api, fields, models, _


class AnalyticalAccountTags(models.Model):
    _inherit = "account.analytic.tag"

    branch_id = fields.Many2one('res.branch', string="Branch", readonly=True)
