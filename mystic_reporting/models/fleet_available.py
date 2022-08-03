from odoo import api, fields, models, _


class FleetAvailable(models.Model):
    _inherit = 'fleet.vehicle'

    def print_report(self):
        fleet_ids = self.search([], limit=1).ids
        return self.env.ref('mystic_reporting.fleet_available_report_pdf').report_action(fleet_ids)

