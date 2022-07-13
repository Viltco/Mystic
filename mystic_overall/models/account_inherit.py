from odoo import api, models, fields


class BranchAccountJournal(models.Model):
    _inherit = "account.journal"

    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True)
    code = fields.Char(string='Short Code', size=10, required=True,
                       help="Shorter name used for display. "
                            "The journal entries of this journal will also be named using this prefix by default." , related="branch_id.code" , readonly=False)

    # @api.onchange('type', 'branch_id', 'code')
    # def _onchange_branch_code(self):
    #     if self.type and self.branch_id:
    #         if self.type == 'sale':
    #             self.code = self.branch_id.code
    #         elif self.type == 'purchase':
    #             self.code = '' + self.branch_id.code
    #         elif self.type == 'cash':
    #             self.code = 'CSH-' + self.branch_id.code
    #         elif self.type == 'bank':
    #             self.code = 'BNK-' + self.branch_id.code
    #         elif self.type == 'general':
    #             self.code = 'MISC-' + self.branch_id.code


class BillAccountRental(models.Model):
    _inherit = "account.move.line"

    rental_id = fields.Many2one('rental.progress', string="Rental", tracking=True)
    date_rental = fields.Datetime('Date')
    rentee_name = fields.Char(string='Rentee Name')


class AccountRental(models.Model):
    _inherit = "account.move"

    rental = fields.Many2many('rental.progress', string="Rental", tracking=True)


class AccountaSSET(models.Model):
    _inherit = "account.asset"

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", tracking=True, copy=False)
    asset_show = fields.Boolean(default=False, copy=False)
    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True, readonly=False)

    @api.onchange("original_move_line_ids")
    def _onchange_branch_id(self):
        self.branch_id = self.original_move_line_ids.branch_id
        self.analytic_tag_ids = self.branch_id.analytical_account_tag_id.ids

    def compute_depreciation_board(self):
        res = super(AccountaSSET, self).compute_depreciation_board()
        for rec in self:
            for dep in rec.depreciation_move_ids:
                dep.write({
                    'branch_id': rec.branch_id.id
                })
        return res
