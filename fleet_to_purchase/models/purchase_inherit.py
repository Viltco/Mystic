from odoo import api, models, fields, _


class PurchaseAnalyticalFleet(models.Model):
    _inherit = "purchase.order.line"

    @api.onchange("product_id")
    def _onchange_analytical_id(self):
        self.account_analytic_id = self.product_id.fleet_vehicle_id.analytical_account_id.id