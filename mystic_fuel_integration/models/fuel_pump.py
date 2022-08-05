from odoo import api, fields, models, _


class FuelPump(models.Model):
    _name = "fuel.pump"
    _description = "Fuel Pump"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')


# class AddFieldsFuel(models.Model):
#     _inherit = "res.partner"
#
#     pump_id = fields.Many2one('fuel.pump', string="Fuel Pump", tracking=True)
#     credit_limit = fields.Integer(string='Credit Limit')


