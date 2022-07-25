from datetime import timedelta, datetime
import pytz
from odoo import models, fields
from pytz import timezone


class RentalProgressInh(models.Model):
    _inherit = 'rental.progress'

    def action_update_roaster(self):
        now_dubai = self.time_out.astimezone(timezone('Asia/Karachi'))
        roaster = self.env['hr.shift.management.line'].search([('rel_management.employee_id.address_home_id','=', self.driver_id.id), ('date','=', self.time_out.date())], limit=1)
        time = now_dubai - timedelta(minutes=30)
        time = time.hour + time.minute / 60.0
        roaster.check_in = time