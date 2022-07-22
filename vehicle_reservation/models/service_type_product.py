from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class ServiceType(models.Model):
    _name = "service.type"
    _description = "Service Type"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    service_lines_id = fields.One2many('service.lines', 'service_type_id', string="Service Lines")

    @api.model
    def default_get(self, fields_list):
        res = super(ServiceType, self).default_get(fields_list)
        vals = [(0, 0, {'service_type': 'hour'}),
                (0, 0, {'service_type': 'daily'}),
                (0, 0, {'service_type': 'weekly'}),
                (0, 0, {'service_type': 'monthly'}),
                (0, 0, {'service_type': 'mobil_oil'}),
                (0, 0, {'service_type': 'oil_filter'}),
                (0, 0, {'service_type': 'air_filter'}),
                (0, 0, {'service_type': 'airport'}),
                (0, 0, {'service_type': 'over_time'}),
                (0, 0, {'service_type': 'over_night'}),
                (0, 0, {'service_type': 'out_station'}),
                ]
        # vals = [(0, 0, {'service_type': 'hour'})]
        res.update({'service_lines_id': vals})
        return res


class ServiceTypeLines(models.Model):
    _name = "service.lines"

    service_type = fields.Selection([
        ('hour', 'Hour'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('mobil_oil', 'Mobil Oil'),
        ('oil_filter', 'Oil Filter'),
        ('air_filter', 'Air Filter'),
        ('airport', 'Airport') ,
        ('over_time', 'OverTime') ,
        ('over_night', 'Over Night') ,
        ('out_station', 'Out station')], string="Service Type")
    pool_id = fields.Many2one('product.product', string="Pool", tracking=True , domain=[('type', '=', 'service')])
    non_pool_id = fields.Many2one('product.product', string="Non Pool", tracking=True, domain=[('type', '=', 'service')])
    non_pool_other_id = fields.Many2one('product.product', string="Non Pool Other", tracking=True, domain=[('type', '=', 'service')])

    service_type_id = fields.Many2one('service.type')
