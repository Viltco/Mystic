from odoo import api, models, fields, _


class PurchaseAnalyticalFleet(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange("product_id")
    def _onchange_analytical_id(self):
        self.account_analytic_id = self.product_id.fleet_vehicle_id.analytical_account_id.id


class PurchaseSource(models.Model):
    _inherit = "purchase.order"

    car_to_purchase_ids = fields.Many2many('po.cars', string="Car To Purchase Source", tracking=True)
    unit_price = fields.Float(string='Unit Price')

    def action_add_price(self):
        for rec in self:
            for r in rec.order_line:
                r.price_unit = rec.unit_price


