from odoo import api, models, fields , _
from odoo.exceptions import UserError


class BranchAccountJournal(models.Model):
    _inherit = "account.journal"

    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True)
    code = fields.Char(string='Short Code', size=10, required=True,
                       help="Shorter name used for display. "
                            "The journal entries of this journal will also be named using this prefix by default.", readonly=False)

    @api.onchange('branch_id')
    def _onchange_branch_code(self):
        for rec in self:
            record = self.env['res.branch'].search([('name', '=' , rec.branch_id.name)])
            print(record)
            self.code = record.code


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
        tags = self.env['account.analytic.tag'].search([('branch_id', '=', self.branch_id.id)])
        self.analytic_tag_ids = tags

    def compute_depreciation_board(self):
        res = super(AccountaSSET, self).compute_depreciation_board()
        for rec in self:
            for dep in rec.depreciation_move_ids:
                dep.write({
                    'branch_id': rec.branch_id.id
                })
        return res

    def set_to_close(self, invoice_line_id, date=None):
        self.ensure_one()
        disposal_date = date or fields.Date.today()
        if invoice_line_id and self.children_ids.filtered(lambda a: a.state in ('draft', 'open') or a.value_residual > 0):
            raise UserError(_("You cannot automate the journal entry for an asset that has a running gross increase. Please use 'Dispose' on the increase(s)."))
        full_asset = self + self.children_ids
        move_ids = full_asset._get_disposal_moves([invoice_line_id] * len(full_asset), disposal_date)
        full_asset.write(
            {'state': 'close'})
        print("Closeddddddddddddddddddddddddddddddddd")
        full_asset.vehicle_id.active = False
        if move_ids:
            return self._return_disposal_view(move_ids)

    # @api.onchange("state")
    # def _onchange_state_id(self):
    #     if self.state == 'close':
    #         print("closed")
    #         self.vehicle_id.active = False
    #     else:
    #         pass
