from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BookingWizard(models.TransientModel):
    _name = "booking.wizard"
    _description = "Booking Wizard"

    partner_id = fields.Many2one('res.partner', string="Customer", tracking=True,
                                 domain=[('partner_type', '=', 'is_customer')])
    # branch_id = fields.Many2one('res.branch', string="Branch", tracking=True)
    booking = fields.Selection([
        ('chauffeur_driven', 'Chauffeur Driven'),
        ('self_drive', 'Self Drive'),
        ('driver', 'Driver')], default='chauffeur_driven', string="Booking")
    based_on = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'), ('yearly', 'Yearly')], default='daily', string="Based On")
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit', 'Credit')], default='cash', string="Payment Type")
    model_id = fields.Many2one('fleet.vehicle.model', string="Model", tracking=True)
    vehicle_out = fields.Datetime('Vehicle Out')
    vehicle_in = fields.Datetime('Vehicle IN')

    def booking_action(self):
        self.env['vehicle.reservation'].create({
            'branch_id': self.env['res.users'].browse(self._uid).branch_id.id,
            'partner_id': self.partner_id.id,
            'booking': self.booking,
            'based_on': self.based_on,
            'payment_type': self.payment_type,
            'model_id': self.model_id.id,
            'vehicle_out': self.vehicle_out,
            'report_timing': self.vehicle_in,
            'state': 'draft',
        })
