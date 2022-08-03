from datetime import timedelta, datetime
import pytz
from odoo import models, fields
from pytz import timezone

from odoo.exceptions import UserError


class RentalProgressInh(models.Model):
    _inherit = 'rental.progress'

    def action_update_roaster(self):
        now_dubai = self.time_out.astimezone(timezone('Asia/Karachi'))
        roaster = self.env['hr.shift.management.line'].search([('rel_management.employee_id.address_home_id','=', self.driver_id.id), ('date','=', self.time_out.date())], limit=1)
        print(roaster)
        if not roaster:
            raise UserError('No Roaster found.')
        arrival_before_departure = datetime.fromtimestamp((roaster.shift_one.arrival_before_departure) * 3600).time()
        print(arrival_before_departure.minute)
        time = now_dubai - timedelta(minutes = arrival_before_departure.minute)
        print('################################################################')
        print(arrival_before_departure)
        time = time.hour + time.minute / 60.0
        print(time)
        roaster.check_in = time