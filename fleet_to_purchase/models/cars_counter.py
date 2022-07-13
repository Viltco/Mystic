from odoo import api, models, fields, _


class CarsCounter(models.Model):
    _name = "cars.counter"
    _description = "Car Counter"
    _rec_name = 'counter'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    number = fields.Char(string='Number')
    counter = fields.Char(string='Car Counter', required=True, copy=False, readonly=True, default='New')

    analytical_account_id = fields.Many2one('account.analytic.account', string="Analytical Account")
    product_id = fields.Many2one('product.product', string="Product")
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", tracking=True, copy=False)

    @api.model
    def create(self, values):
        print(values)
        values['counter'] = self.env['ir.sequence'].next_by_code('cars.counter') or _('New')
        return super(CarsCounter, self).create(values)





