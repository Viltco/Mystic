from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ChauffeurWizard(models.TransientModel):
    _name = "chauffeur.wizard"
    _description = "Chauffeur Wizard"

    driver_id = fields.Many2one('res.partner', string="Driver", tracking=True,
                                domain=[('partner_type', '=', 'is_driver')])
    odometer = fields.Integer(string='Current Meter Reading' , readonly=True)
    km_out = fields.Integer(string="Kms Out", tracking=True)
    time_out = fields.Datetime('Time Out')

    def chauffeur_action(self):
        print("u click")
        for rec in self:
            record = self.env['rental.progress'].browse(self.env.context.get('active_id'))
            if rec.km_out > 0:
                record.driver_id = self.driver_id.id
                record.km_out = self.km_out
                record.time_out = self.time_out
                record.state = 'chauffeur_out'
                r = rec.env['fleet.vehicle.state'].search([('sequence', '=', 2)])
                record.vehicle_no.state_id = r.id
            else:
                raise ValidationError(f'Please enter some value of KM OUT')


