from datetime import datetime
from odoo import api, fields, models, _


class MoveWizard(models.TransientModel):
    _name = "move.wizard"
    _description = "Move Wizard"

    move_date = fields.Datetime('Move Date')
    current_meter_reading = fields.Integer('Current Meter Reading')

    def move_wizard_action(self):
        record = self.env['nonrevenue.ticket'].browse(self.env.context.get('active_id'))
        record.move_date = self.move_date
        record.current_meter_reading = self.current_meter_reading
        record.state = 'fleet_moved'
        r = self.env['fleet.vehicle.state'].search([('sequence', '=', 3)])
        record.vehicle_id.state_id = r.id




