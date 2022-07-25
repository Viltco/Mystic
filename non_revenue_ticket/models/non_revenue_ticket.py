from datetime import datetime

from odoo import api, models, fields, _


class NonRevenueTicketFleet(models.Model):
    _name = "nonrevenue.ticket"
    _description = "Non Revenue Ticket"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'number'

    number = fields.Char(string='Number', required=True, copy=False, readonly=True, default='New')
    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True,
                                default=lambda self: self.env.user.branch_id)
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", tracking=True)
    brand_ids = fields.Many2many('fleet.vehicle', compute="_compute_brand_ids")
    purpose = fields.Text(string='Purpose')
    move_date = fields.Datetime('Move Date')
    current_meter_reading = fields.Integer('Current Meter Reading')
    return_date = fields.Datetime('Return Date')
    meter_milage = fields.Integer('Meter Milage')
    driven = fields.Integer('Driven')
    created_on = fields.Datetime('Created On',default=datetime.today())


    state = fields.Selection(
        [('new', 'New'), ('fleet_moved', 'Fleet Moved'),
         ('fleet_returned', 'Fleet Returned'), ('cancel', 'Cancelled')],
        default='new',
        string="State", tracking=True)

    @api.model
    def create(self, values):
        if 'branch_id' in values:
            seq = self.env['ir.sequence'].search(
                [('name', '=', 'Non Revenue Ticket'), ('branch_id', '=', values['branch_id'])])
            self.env['ir.sequence'].next_by_code(seq.code)
            values['number'] = seq.prefix + '-' + seq.branch_id.code + '-' + str(seq.number_next_actual) or _('New')
        return super(NonRevenueTicketFleet, self).create(values)

    def action_move(self):
        return {
            'name': _('Move'),
            'res_model': 'move.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'nonrevenue.ticket',
                'active_ids': self.ids,
                'default_current_meter_reading': self.vehicle_id.odometer,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.depends('vehicle_id')
    def _compute_brand_ids(self):
        for rec in self:
            records = self.env['fleet.vehicle'].search([])
            vehicle_list = []
            if records:
                for re in records:
                    if re.state_id.sequence in [0]:
                        vehicle_list.append(re.id)
                        rec.brand_ids = vehicle_list
                    else:
                        rec.brand_ids = []
            else:
                rec.brand_ids = []

    def action_return(self):
        return {
            'name': _('Return'),
            'res_model': 'return.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'nonrevenue.ticket',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_reset_to_draft(self):
        self.state = 'new'

    def action_cancel(self):
        self.state = 'cancel'

