# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
from datetime import date
from datetime import time

class AttendanceShift(models.Model):
    _name = 'hr.shift'
    _description = 'This table handle the data of shift addition in attendance'
    _rec_name = 'shift_name'

    shift_name = fields.Char(string='Shift Name', required=True)
    shift_desc = fields.Char(string='Description')
    time_in = fields.Float(string='Time In', required=True)
    time_out = fields.Float(string='Time Out', required=True)
    shift_duration = fields.Float(string='Shift Duration', compute='compute_shift_duration')
    company = fields.Many2one('res.company', string='Company', required=True)
    location = fields.Many2one('res.partner', string='Location')
    department = fields.Many2one('hr.department', string='Department')
    grace_period = fields.Float(string='Grace Period', required=True)
    min_hours_halfday = fields.Float(string='Min Hours for Half Day')
    min_hours_fullday = fields.Float(string='Min Hours for Full Day')

    shift_type = fields.Selection([
        ('general', 'General'),
        ('morning', 'Morning'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ], string='Shift Type', required=True, copy=False, index=True, tracking=3, default='general')

    is_night_shift = fields.Boolean('Is Night Shift?')
    is_overtime_allowed = fields.Boolean('Is Overtime Allowed?')
    is_driver_shift = fields.Boolean('Is Driver Shift?')
    arrival_before_departure = fields.Float(string='Arrival Before Departure')
    early_in = fields.Float(string='Early In Threshold')
    late_out = fields.Float(string='Late out Threshold')

    branch_id = fields.Many2one('res.branch')

    # @api.onchange('time_in', 'time_out')
    # def _onchange_hours(self):
    #     # avoid negative or after midnight
    #     self.time_in = min(self.time_in, 23.99)
    #     self.time_in = max(self.time_in, 0.0)
    #
    #     self.time_out = min(self.time_out, 23.99)
    #     self.time_out = max(self.time_out, 0.0)
    #
    #     # avoid wrong order
    #     self.time_out = max(self.time_out, self.time_in)



    @api.onchange('min_hours_halfday')
    def _onchange_min_hours_halfday(self):
        # avoid negative or after midnight
        self.min_hours_halfday = min(self.min_hours_halfday, 23.99)
        self.min_hours_halfday = max(self.min_hours_halfday, 0.0)



    @api.onchange('min_hours_fullday')
    def _onchange_min_hours_fullday(self):
        # avoid negative or after midnight
        self.min_hours_fullday = min(self.min_hours_fullday, 23.99)
        self.min_hours_fullday = max(self.min_hours_fullday, 0.0)



    @api.onchange('grace_period')
    def _onchange_grace_period(self):
        # avoid negative or after midnight
        self.grace_period = min(self.grace_period, 23.99)
        self.grace_period = max(self.grace_period, 0.0)



    def compute_shift_duration(self):
        time = self.time_out - self.time_in
        self.shift_duration = time