from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RegisterWizard(models.TransientModel):
    _name = "register.wizard"
    _description = "Register Wizard"

    license_plate = fields.Char(string='License Plate')
    analytical_account_id = fields.Many2one('account.analytic.account', string="Analytical Account")
    product_id = fields.Many2one('product.product', string="Product")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", tracking=True, copy=False)

    def register_action(self):
        rec = self.env['po.cars'].browse(self.env.context.get('active_id'))

        self.vehicle_id.license_plate = self.license_plate
        print(self.vehicle_id.license_plate)
        print('hhh')
        self.vehicle_id.product_id.name = self.license_plate
        self.vehicle_id.analytical_account_id.name = self.license_plate
        rec.button_show = True
        self.vehicle_id.active = True










