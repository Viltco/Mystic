from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CarRegisterTreeView(models.TransientModel):
    _name = "car.tree"
    _description = "Car Register Tree"

    license_plate = fields.Char(string='License Plate')
    _sql_constraints = [
        ('license_plate_unique', 'unique(license_plate)', 'Cant be duplicate value For License Plate!')]
    car_counter_id = fields.Many2one('cars.counter', string="Cars")
    register_id = fields.Many2one('register.wizard')












