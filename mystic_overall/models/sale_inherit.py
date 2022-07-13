from odoo import api, models, fields, _


class SaleOrderFleet(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        res = super(SaleOrderFleet, self)._prepare_invoice()
        res['branch_id'] = self.branch_id.id
        return res

