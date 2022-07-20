from odoo import fields, models, api, _
from datetime import timedelta
from datetime import datetime
from datetime import timezone
import pytz


class AttendanceInherited(models.Model):
    _inherit = 'hr.attendance'

    early_in = fields.Float('Early In', compute='_compute_time_in')
    late_in = fields.Float('Late In', compute='_compute_time_in')
    early_out = fields.Float('Early Out', compute='_compute_time_out')
    late_out = fields.Float('Late Out', compute='_compute_time_out')
    shift = fields.Char('Shift', compute='_compute_shift')

    @api.depends('check_in')
    def _compute_time_in(self):
        for rec in self:
            if rec.check_in:
                roaster = self.env['hr.shift.management.line'].search(
                    [('rel_management.employee_id', '=', rec.employee_id.id), ('date', '=', rec.check_in.date())])
                roaster_check_in = datetime.fromtimestamp((roaster.check_in) * 3600).time()

                # Change Time Zone
                utc = pytz.timezone('UTC')
                localtz = pytz.timezone('Asia/Karachi')
                utctime = utc.localize(rec.check_in)
                localtime = localtz.normalize(utctime.astimezone(localtz))

                start_time = roaster_check_in
                stop_time = localtime.time()

                date = roaster.date
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

    @api.depends('check_out')
    def _compute_time_out(self):
        for rec in self:
            if rec.check_out:
                roaster = self.env['hr.shift.management.line'].search(
                    [('rel_management.employee_id', '=', rec.employee_id.id), ('date', '=', rec.check_out.date())])
                roaster_check_out = datetime.fromtimestamp((roaster.check_out) * 3600).time()

                # Change Time Zone
                utc = pytz.timezone('UTC')
                localtz = pytz.timezone('Asia/Karachi')
                utctime = utc.localize(rec.check_out)
                localtime = localtz.normalize(utctime.astimezone(localtz))

                start_time = roaster_check_out
                stop_time = localtime.time()

                date = roaster.date
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
                print(roaster)
                check_in = str(roaster.check_in).replace('.', ':') + '0'
                check_out = str(roaster.check_out).replace('.', ':') + '0'
                date = str(roaster.date).replace('-', '/')
                rec.shift = f'{date} - {check_in} - {check_out}'
