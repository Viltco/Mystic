from odoo import api, fields, models, _


class Contracts(models.Model):
    _name = "res.contract"
    _description = "ResContracts"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', copy=False, readonly=True, default='New')
    partner_id = fields.Many2one('res.partner', string="Customer")
    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True, required=True)
    apply_over_time = fields.Integer(string='Apply Over Time After')
    apply_over_night = fields.Integer(string='Apply Over Night After')
    apply_out_station = fields.Integer(string='Apply Out Station After')

    state = fields.Selection([('draft', 'Draft'), ('confirm', 'confirmed'), ('cancel', 'Cancelled')], default='draft',
                             string="status", tracking=True)
    contract_lines_id = fields.One2many('contract.lines', 'contract_id', string='Contract Lines')

    @api.model
    def create(self, values):
        if 'branch_id' in values:
            seq = self.env['ir.sequence'].search(
                [('name', '=', 'Customer Contracts'), ('branch_id', '=', values['branch_id'])])
            self.env['ir.sequence'].next_by_code(seq.code)
            values['name'] = seq.prefix + '-' + seq.branch_id.code + '-' + str(seq.number_next_actual) or _('New')
        return super(Contracts, self).create(values)

    def action_confirm(self):
        self.state = 'confirm'

    def action_reset_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'


class ContractLines(models.Model):
    _name = "contract.lines"
    _description = "Contracts Lines"

    model_id = fields.Many2one('fleet.vehicle.model', string="Model", tracking=True)
    per_hour_rate = fields.Float(string='Hour')
    per_km_rate = fields.Float(string='KM')
    per_day_rate = fields.Float(string='Daily')
    per_week_rate = fields.Float(string='Weekly')
    per_month_rate = fields.Float(string='Monthly')
    per_year_rate = fields.Float(string='Yearly')
    over_time = fields.Float(string='OverTime')
    over_night = fields.Float(string='OverNight')
    out_station = fields.Float(string='OutStation')
    contract_id = fields.Many2one('res.contract')
