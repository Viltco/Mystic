# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from datetime import date
from datetime import time
from dateutil.relativedelta import relativedelta

class AllocationShift(models.Model):
    _name = 'hr.shift.allocation'
    _description = 'This table handle the data of shift allocation in attendance'
    _rec_name = 'name'

    name = fields.Char(string='Name', readonly=True)
    employee_id = fields.Many2many('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)
    is_proceed = fields.Boolean(default=False)
    shift_id = fields.Many2one('hr.shift')
    branch_id = fields.Many2one('res.branch')

    # max_shift_day = fields.Selection([
    #     ('1', '1'),
    #     ('2', '2'),
    # ], string='Max Shifts/Day', required=True, copy=False, index=True, tracking=3, default='1')

    allocation_lines = fields.One2many('hr.shift.allocation.line', 'rel_allocation')

    def action_add_shift(self):
        start = "01:00"
        end = "08:59"
        start_dt = datetime.strptime(start, '%H:%M')
        end_dt = datetime.strptime(end, '%H:%M')
        diff = end_dt-start_dt
        seconds = diff.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        print(hours)
        print(minutes)
        print(seconds)
        for line in self.allocation_lines:
            line.shift_one_type = self.shift_id.id

    @api.onchange('department_id', 'branch_id')
    def onchange_department_id(self):
        employees = []
        if self.department_id.id and self.branch_id.id:
            employees = self.env['hr.employee'].search([('department_id', '=', self.department_id.id)])
        elif self.department_id.id:
            employees = self.env['hr.employee'].search(
                [('department_id', '=', self.department_id.id)])
        elif self.branch_id.id:
            employees = self.env['hr.employee'].search(
                [('branch_id', '=', self.branch_id.id)])
        print(employees)
        if employees:
            self.employee_id = employees.ids
        else:
            print('ff')
            self.employee_id = False

    # def unlink(self):
    #     if not self.env.user.has_group('de_shift_attendance.allow_parent_allocation_deletion'):
    #         raise UserError(('You Did Not Have Access Rights to Delete The Record '))
    #     else:
    #         super(AllocationShift,self).unlink()

    # @api.onchange('max_shift_day')
    # def show_shifts(self):
    #     if self.max_shift_day == '1':
    #         self.allocation_lines.hide_field = True

    @api.onchange('date_start','date_end')
    def create_records(self):
        for line in self.allocation_lines:
            line.unlink()
        if self.date_start and self.date_end:
            delta = self.date_start - self.date_end
            total_days = abs(delta.days)
            for i in range(0, total_days + 1):
                date_after_month = self.date_start + relativedelta(days=i)
                day_week = '0'
                if date_after_month.weekday() == 0:
                    day_week = '0'
                elif date_after_month.weekday() == 1:
                    day_week = '1'
                elif date_after_month.weekday() == 2:
                    day_week = '2'
                elif date_after_month.weekday() == 3:
                    day_week = '3'
                elif date_after_month.weekday() == 4:
                    day_week = '4'
                elif date_after_month.weekday() == 5:
                    day_week = '5'
                elif date_after_month.weekday() == 6:
                    day_week = '6'
                vals = {
                    'rel_allocation': self.id,
                    'date': date_after_month,
                    'day': day_week,
                }
                self.env['hr.shift.allocation.line'].create(vals)
                i = i + 1

    @api.model
    def create(self, vals):
        if vals.get('name', ('New')) == ('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.shift.allocation.sequence') or _('New')
        result = super(AllocationShift, self).create(vals)
        return result

    def create_management_data(self):
        self.is_proceed = True
        for employee in self.employee_id:
            line_vals = []
            for line in self.allocation_lines:
                line_vals.append((0,0, {
                    'rel_management': line.id,
                    'date': line.date,
                    'shift_one': line.shift_one_type.id,
                    'check_in': line.shift_one_type.time_in,
                    'check_out': line.shift_one_type.time_out,
                    'shift_two': line.shift_two_type.id,
                    'rest_day': line.rest_day,
                    'day': line.day,
                }))
            vals = {
                'employee_id': employee.id,
                'name': self.name,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'management_lines': line_vals
            }
            lines = self.env['hr.shift.management'].create(vals)


class AllocationShiftLine(models.Model):
    _name = 'hr.shift.allocation.line'

    rel_allocation = fields.Many2one('hr.shift.allocation')
    date = fields.Date(string='Date')
    shift_one = fields.Boolean(string='Shift 1', default=True)
    shift_one_type = fields.Many2one('hr.shift', string='Shift 1 Type')
    shift_two = fields.Boolean(string='Shift 2', default=False)
    shift_two_type = fields.Many2one('hr.shift', string='Shift 2 Type')
    # hide_field = fields.Boolean(string='Hide', default=False, readonly=True)
    rest_day = fields.Boolean(string='Rest Day')
    day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='Day',copy=False, default='0')

    # def get_day(date_string):
    #     date = datetime.strptime(date_string, '%Y-%m-%d')
    #     print('_______________________',date)
    #     return date.day

    @api.onchange('rest_day')
    def _onchange_rest_day(self):
        for line in self:
            if line.rest_day == True:
                line.shift_one = False
                line.shift_two = False
            else:
                line.shift_one = True
                line.shift_two = True

    def unlink(self):
        if not self.env.user.has_group('de_shift_attendance.allow_allocation_deletion'):
            raise UserError(('You Did Not Have Access Rights to Delete The Record '))
        else:
            super(AllocationShiftLine,self).unlink()


