from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class RentalMoves(models.Model):
    _inherit = "account.move"

    rental_lines_id = fields.One2many('rental.move.line', 'rental_move_id', string="Rental Lines")


class ServiceTypeLines(models.Model):
    _name = "rental.move.line"

    date_rental = fields.Date('Date')
    rental_id = fields.Many2one('rental.progress', string="Rental")
    description = fields.Char(string="Description")
    rentee_name = fields.Char(string='Rentee Name')
    amount = fields.Integer(string='Amount')

    rental_move_id = fields.Many2one('account.move')
