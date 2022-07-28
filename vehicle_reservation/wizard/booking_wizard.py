from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BookingWizard(models.TransientModel):
    _name = "booking.wizard"
    _description = "Booking Wizard"

    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True)
    partner_id = fields.Many2one('res.partner', string="Customer", tracking=True,
                                 domain=[('partner_type', '=', 'is_customer')])
    # branch_id = fields.Many2one('res.branch', string="Branch", tracking=True)
    booking = fields.Selection([
        ('chauffeur_driven', 'Chauffeur Driven'),
        ('self_drive', 'Self Drive'),
        ('driver', 'Driver')], default='chauffeur_driven', string="Booking")
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit', 'Credit')], default='cash', string="Payment Type")
    pickup = fields.Text(string='Pickup')
    program = fields.Text(string='Program')
    model_id = fields.Many2one('fleet.vehicle.model', string="Model", tracking=True)
    vehicle_out = fields.Datetime('Vehicle Out')
    vehicle_in = fields.Datetime('Vehicle IN')

    def booking_action(self):
        self.env['vehicle.reservation'].create({
            'branch_id': self.branch_id.id,
            'partner_id': self.partner_id.id,
            'booking': self.booking,
            'payment_type': self.payment_type,
            'model_id': self.model_id.id,
            'vehicle_out': self.vehicle_out,
            'report_timing': self.vehicle_in,
            'pickup': self.pickup,
            'program': self.program,
            'state': 'draft',
        })
