from odoo import fields, models, api, _
from datetime import timedelta
from datetime import datetime
from datetime import timezone
import pytz


class AttendanceInherited(models.Model):
    _inherit = 'hr.attendance'

    # early_in = fields.Float('Early In', compute='_compute_time_in')
    # late_in = fields.Float('Late In', compute='_compute_time_in')
    # early_out = fields.Float('Early Out', compute='_compute_time_out')
    # late_out = fields.Float('Late Out', compute='_compute_time_out')
    shift = fields.Char('Shift', compute='_compute_shift')
    extra_time = fields.Float('Extra Time', compute='_compute_extra_time')
    short_time = fields.Float('Short Time', compute='_compute_short_time')
    overtime = fields.Float('Over Time', compute='_compute_over_time')
    branch_id = fields.Many2one('res.branch', compute='_compute_data')
    #
    early_in = fields.Float('Early In')
    late_in = fields.Float('Late In')
    early_out = fields.Float('Early Out')
    late_out = fields.Float('Late Out')
    # shift = fields.Char('Shift')
    # extra_time = fields.Float('Extra Time')
    # short_time = fields.Float('Short Time')
    # overtime = fields.Float('Over Time')
    # Counters
    rental_count = fields.Integer(string='Rental Count')
    osa_count = fields.Integer(string='OSA')
    loc_night_count = fields.Integer(string='Local Night')
    out_night_count = fields.Integer(string='Out Night')
    rakhsha_count = fields.Integer(string='Rakhsha')
    rest_day = fields.Integer('O/G/H')

    def change_time_zone(self, time):
        if time:
            utc = pytz.timezone('UTC')
            localtz = pytz.timezone('Asia/Karachi')
            utctime = utc.localize(time)
            time = localtz.normalize(utctime.astimezone(localtz))
        return time

    # @api.depends('check_in')
    # def _compute_time_in(self):
    @api.onchange('check_in')
    def _onchange_time_in(self):
        for rec in self:
            if rec.check_in:
                roaster = self.env['hr.shift.management.line'].search(
                    [('rel_management.employee_id', '=', rec.employee_id.id), ('date', '=', rec.check_in.date())])
                if roaster:
                    for rost in roaster:
                        roaster_check_in = datetime.fromtimestamp((rost.check_in) * 3600).time()
                        # Change Time Zone

                        localtime = self.change_time_zone(rec.check_in)

                        start_time = roaster_check_in
                        stop_time = localtime.time()

                        date = rost.date
                        datetime1 = datetime.combine(date, start_time)
                        datetime2 = datetime.combine(date, stop_time)
                        time_elapsed = datetime1 - datetime2
                        total_time = time_elapsed.total_seconds() / 3600.0
                        if total_time > 0:
                            rec.early_in = abs(total_time)
                            rec.late_in = False
                        else:
                            rec.late_in = abs(total_time)
                            rec.early_in = False
                else:
                    rec.early_in = False
                    rec.late_in = False

    # @api.depends('check_out')
    # def _compute_time_out(self):
    @api.onchange('check_out')
    def _onchange_time_out(self):
        for rec in self:
            if rec.check_out:
                roaster = self.env['hr.shift.management.line'].search(
                    [('rel_management.employee_id', '=', rec.employee_id.id), ('date', '=', rec.check_out.date())])
                if roaster:
                    for rost in roaster:
                        roaster_check_out = datetime.fromtimestamp((rost.check_out) * 3600).time()

                        # Change Time Zone
                        utc = pytz.timezone('UTC')
                        localtz = pytz.timezone('Asia/Karachi')
                        utctime = utc.localize(rec.check_out)
                        localtime = localtz.normalize(utctime.astimezone(localtz))

                        start_time = roaster_check_out
                        stop_time = localtime.time()

                        date = rost.date
                        datetime1 = datetime.combine(date, start_time)
                        datetime2 = datetime.combine(date, stop_time)
                        time_elapsed = datetime1 - datetime2
                        if rec.check_in.date() == rec.check_out.date():
                            print('same dates')
                            total_time = time_elapsed.total_seconds() / 3600.0
                            if total_time > 0:
                                rec.early_out = abs(total_time)
                                rec.late_out = False
                            else:
                                rec.late_out = abs(total_time)
                                rec.early_out = False
                        else:
                            print('different dates')
                            total_time = (time_elapsed.total_seconds() / 3600.0) - 12
                            if total_time > 0:
                                rec.early_out = total_time
                                rec.late_out = False
                            else:
                                rec.late_out = abs(total_time)
                                rec.early_out = False
                else:
                    rec.early_out = False
                    rec.late_out = False

    @api.depends('employee_id')
    def _compute_shift(self):
        for rec in self:
            if rec.employee_id:
                roaster = self.env['hr.shift.management.line'].search(
                    [('rel_management.employee_id', '=', rec.employee_id.id), ('date', '=', rec.check_in.date())])
                if roaster:
                    for rost in roaster:
                        check_in = str(rost.check_in).replace('.', ':') + '0'
                        check_out = str(rost.check_out).replace('.', ':') + '0'
                        date = str(rost.date).replace('-', '/')
                        rec.shift = f'{date} - {check_in} - {check_out}'
                else:
                    rec.shift = None

    @api.depends('early_in', 'late_out')
    def _compute_extra_time(self):
        for rec in self:
            rec.extra_time = rec.early_in + rec.late_out
            rec._onchange_time_in()
            rec._onchange_time_out()

    @api.depends('early_out', 'late_in')
    def _compute_short_time(self):
        for rec in self:
            rec.short_time = rec.early_out + rec.late_in

    @api.depends('extra_time', 'short_time')
    def _compute_over_time(self):
        for rec in self:
            rec.overtime = rec.extra_time - rec.short_time

    @api.depends('employee_id')
    def _compute_data(self):
        for rec in self:
            emp = self.env['res.partner'].search([('name', '=', rec.employee_id.name)])
            rentals = self.env['rental.progress'].search(
                [('driver_id.name', '=', rec.employee_id.name),
                 ('state', '=', 'rental_close')])
            print(rentals)
            total_rc = 0
            total_osa = 0
            total_ln = 0
            total_on = 0
            for rc in rentals:
                local_time_out = self.change_time_zone(rc.time_out)
                local_check_in = self.change_time_zone(rc.time_out)
                if local_time_out == local_check_in:
                    print('Rental Find')
                    total_rc += 1
                    if rc.out_of_station:
                        total_osa += 1
                        if rc.over_night:
                            total_on += 1
                    else:
                        if rc.over_night:
                            total_ln += 1
            rec.rental_count = total_rc
            rec.osa_count = total_osa
            rec.loc_night_count = total_ln
            rec.out_night_count = total_on
            for branch in emp:
                rec.branch_id = branch.branch_id.id

            #             Day off
            if rec.check_in:
                roaster = self.env['hr.shift.management.line'].search(
                    [('rel_management.employee_id', '=', rec.employee_id.id), ('date', '=', rec.check_in.date())])
                if roaster:
                    for rost in roaster:
                        print('rest day')
                        if rost.rest_day:
                            print('rest day')
                            rec.rest_day = 1
                        else:
                            rec.rest_day = 0

            # #             # Rakisha
            # total_rakisha = 0
            # if rec.check_in:
            #     roaster = self.env['hr.shift.management.line'].search(
            #         [('rel_management.employee_id', '=', rec.employee_id.id), ('date', '=', rec.check_in.date())])
            #     if roaster:
            #         for rost in roaster:
            #             roaster_check_in = datetime.fromtimestamp((rost.check_in) * 3600).time()
            #             shift_early_in = datetime.fromtimestamp((rost.shift_one.early_in) * 3600).time()
            #             att_check_in = self.change_time_zone(rec.check_in).time()
            #             att_check_out = self.change_time_zone(rec.check_out).time()
            #             shift_late_out = datetime.fromtimestamp((rost.shift_one.late_out) * 3600).time()
            #             print(f'att_check_in: {att_check_in}')
            #             print(f'roaster_check_in {roaster_check_in}')
            #             print(f'shift_early_in {shift_early_in}')
            #             print(f'att_check_out {att_check_out}')
            #             print(f'shift_late_out {shift_late_out}')
            #             if att_check_in <= shift_early_in:
            #                 print('att_check_in <= shift_early_in')
            #                 rental = self.env['rental.progress'].search(
            #                     [('driver_id.name', '=', rec.employee_id.name)])
            #                 if rental:
            #                     for ren in rental:
            #                         if ren:
            #                             rental_time_out = self.change_time_zone(ren.time_out).time()
            #                             print(f'rental_time_out {rental_time_out}')
            #                             arrival_before_departure = datetime.fromtimestamp(
            #                                 (rost.shift_one.arrival_before_departure) * 3600).time()
            #                             print(f'arrival_before_departure {arrival_before_departure}')
            #                             date = rost.date
            #                             datetime1 = datetime.combine(date, rental_time_out)
            #                             datetime2 = datetime.combine(date, arrival_before_departure)
            #                             time_elapsed = datetime1 - datetime2
            #
            #                             time_elapsed = datetime.fromtimestamp(
            #                                 (time_elapsed.total_seconds() / 3600) * 3600).time()
            #                             print(f'time_elapsed {time_elapsed}')
            #                             if time_elapsed <= shift_early_in:
            #                                 print('time_elapsed <= shift_early_in')
            #                                 if rec.check_in.date() == rost.date and ren.time_out.date() == rec.check_in.date():
            #                                     total_rakisha += 1
            #             if att_check_out >= shift_late_out:
            #                 print('att_check_out >= shift_late_out')
            #                 rental = self.env['rental.progress'].search(
            #                     [('driver_id.name', '=', rec.employee_id.name)])
            #                 print(rental)
            #                 if rental:
            #                     for ren in rental:
            #                         if ren.time_out.date() == rost.date:
            #                             rental_time_in = self.change_time_zone(ren.time_in).time()
            #                             print(f'rental_time_in {rental_time_in}')
            #                             if rental_time_in >= shift_late_out:
            #                                 print('rental_time_in >= shift_late_out')
            #                                 total_rakisha += 1
            # rec.rakhsha_count = total_rakisha
