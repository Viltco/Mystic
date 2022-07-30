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

    rentee_type = fields.Selection([
        ('mr', 'MR.'),
        ('mrs', 'MRS.'),
        ('prof', 'Prof.'),
        ('dr', 'Dr.'),
    ], default='mr', string="Rentee Name")
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    rentee_mobile_number = fields.Char(string='Rentee Mobile Number')
    source_name = fields.Char(string='Source Name')
    source_mobile_number = fields.Char(string='Source Mobile Number')

    def booking_action(self):
        self.env['vehicle.reservation'].create({
            'branch_id': self.branch_id.id,
            'partner_id': self.partner_id.id,
            'booking': self.booking,
            'payment_type': self.payment_type,
            'model_id': self.model_id.id,
            'vehicle_out': self.vehicle_out,
            'rentee_type': self.rentee_type,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'rentee_mobile_number': self.rentee_mobile_number,
            'source_name': self.source_name,
            'source_mobile_number': self.source_mobile_number,
            'report_timing': self.vehicle_in,
            'pickup': self.pickup,
            'program': self.program,
            'state': 'draft',
        })
