from odoo import api, models, fields


class FleetProduct(models.Model):
    _inherit = "product.product"

    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")


class FleetProductTemplate(models.Model):
    _inherit = "product.template"

    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

