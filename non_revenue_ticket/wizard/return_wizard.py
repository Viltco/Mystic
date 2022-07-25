from datetime import datetime
from odoo import api, fields, models, _


class ReturnWizard(models.TransientModel):
    _name = "return.wizard"
    _description = "Return Wizard"

    return_date = fields.Datetime('Return Date')
    meter_milage = fields.Integer('Meter Milage')

    def return_wizard_action(self):
        record = self.env['nonrevenue.ticket'].browse(self.env.context.get('active_id'))
        record.vehicle_id.odometer = self.meter_milage
        record.meter_milage = self.meter_milage
        record.return_date = self.return_date
        record.state = 'fleet_returned'
        record.driven = self.meter_milage - record.current_meter_reading
        r = self.env['fleet.vehicle.state'].search([('sequence', '=', 0)])
        record.vehicle_id.state_id = r.id




