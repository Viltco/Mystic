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

    addit_hour_rate = fields.Integer(string='Additional Hourly Rate')
    hourly_limit = fields.Integer(string='Hourly Limit')
    addit_km_rate = fields.Integer(string='Additional KM Rate')
    km_limit = fields.Integer(string='KM Limit')

    per_hour_rate = fields.Float(string='Hour')
    per_km_rate = fields.Float(string='KM')
    per_day_rate = fields.Float(string='Daily')
    per_week_rate = fields.Float(string='Weekly')
    per_month_rate = fields.Float(string='Monthly')
    mobil_oil_rate = fields.Float(string='Mobil Oil Rate')
    oil_filter_rate = fields.Float(string='Oil Filter Rate')
    air_filter_rate = fields.Float(string='Air Filter Rate')
    airport_rate = fields.Float(string='Airport')
    over_time = fields.Float(string='OverTime')
    over_night = fields.Float(string='OverNight')
    out_station = fields.Float(string='OutStation')

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

    def action_server_lock(self):
        print("u click")
        active_model = self.env['res.contract'].browse(self.env.context.get('active_id'))
        for r in active_model.contract_lines_id:
            print(r)
            r.is_lock = True
            # if not r.is_lock:
            #     r.is_lock = True
            # else:
            #     r.is_lock = False

    def action_server_unlock(self):
        print("u click")
        active_model = self.env['res.contract'].browse(self.env.context.get('active_id'))
        for r in active_model.contract_lines_id:
            print(r)
            r.is_lock = False

            # if not r.is_lock:
            #     r.is_lock = True
            # else:
            #     r.is_lock = False

    def action_add_price(self):
        for rec in self:
            for r in rec.contract_lines_id:
                if not r.is_lock:
                    print(r)
                    r.per_hour_rate = rec.per_hour_rate
                    r.per_km_rate = rec.per_km_rate
                    r.per_day_rate = rec.per_day_rate
                    r.per_week_rate = rec.per_week_rate
                    r.per_month_rate = rec.per_month_rate
                    r.mobil_oil_rate = rec.mobil_oil_rate
                    r.oil_filter_rate = rec.oil_filter_rate
                    r.air_filter_rate = rec.air_filter_rate
                    r.airport_rate = rec.airport_rate
                    r.over_time = rec.over_time
                    r.over_night = rec.over_night
                    r.out_station = rec.out_station
                else:
                    print("no change")


class ContractLines(models.Model):
    _name = "contract.lines"
    _description = "Contracts Lines"

    model_id = fields.Many2one('fleet.vehicle.model', string="Model", tracking=True)
    per_hour_rate = fields.Float(string='Hour')
    per_km_rate = fields.Float(string='KM')
    per_day_rate = fields.Float(string='Daily')
    per_week_rate = fields.Float(string='Weekly')
    per_month_rate = fields.Float(string='Monthly')
    mobil_oil_rate = fields.Float(string='Mobil Oil Rate')
    oil_filter_rate = fields.Float(string='Oil Filter Rate')
    air_filter_rate = fields.Float(string='Air Filter Rate')
    airport_rate = fields.Float(string='Airport')
    over_time = fields.Float(string='OverTime')
    over_night = fields.Float(string='OverNight')
    out_station = fields.Float(string='OutStation')
    contract_id = fields.Many2one('res.contract')

    is_lock = fields.Boolean(default=False)
