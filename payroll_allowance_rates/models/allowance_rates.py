# # -*- coding: utf-8 -*-
#
from odoo import models, fields, api


class PayrollAllowanceRates(models.Model):
    _name = 'allowance.rates'
    _rec_name = 'early_in'

    early_in = fields.Float('O/T Hrs (Early In)')
    late_out = fields.Float('O/T Hrs (Late Out)')
    out_station = fields.Integer('OSA (Out of Station Allowance)')
    local_night = fields.Integer('L/N (Local Night)')
    out_night = fields.Integer('O/N (Out Night)')
    over_days = fields.Float('Over Days & G/H')
    rakhsha = fields.Integer('Rakhsha')
    rentals = fields.Integer('Rentals')
    monthly_nights = fields.Integer('Monthly Nights')
    extra = fields.Integer('Extra')
    hold_night = fields.Integer('Hold Night')
