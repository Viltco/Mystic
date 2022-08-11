from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ChauffeurInWizard(models.TransientModel):
    _name = "chauffeur.in"
    _description = "Chauffeur In Wizard"

    km_in = fields.Integer(string="Kms In", tracking=True)
    time_in = fields.Datetime('Time In')
    toll = fields.Integer(string="Toll", tracking=True)
    allowa = fields.Integer(string="Allowa.", tracking=True)
    m_tag = fields.Integer(string="M-Tag", tracking=True)
    damage_charges = fields.Integer(string="Damage Charges (Depreciation)", tracking=True)
    note = fields.Text(string='Note')


    # def chauffeur_in_action(self):
    #     print("u click")
    #     for rec in self:
    #         record = self.env['rental.progress'].browse(self.env.context.get('active_id'))
    #         if rec.km_in > record.km_out:
    #             record.km_in = rec.km_in
    #             record.time_in = rec.time_in
    #             record.state = 'chauffeur_in'
    #             result = self.env['res.contract'].search(
    #                 [('partner_id', '=', record.name.id),('state', '=', 'confirm')])
    #             i = 0
    #             for r in result.contract_lines_id:
    #                 if r.model_id.id == record.vehicle_no.model_id.id:
    #                     if r.model_id.model_year == record.vehicle_no.model_id.model_year:
    #                         # if record.based_on == 'daily':
    #                         #     i = r.per_day_rate
    #                         # elif record.based_on == 'weekly':
    #                         #     i = r.per_week_rate
    #                         # elif record.based_on == 'monthly':
    #                         #     i = r.per_month_rate
    #                         # vals = {
    #                         #     'partner_id': record.name.id,
    #                         #     'vehicle_id': record.vehicle_no.id,
    #                         #     'rental_id': record.id,
    #                         #     'start_date': record.time_out,
    #                         #     'expiration_date': rec.time_in,
    #                         #     'cost_frequency': record.based_on,
    #                         #     'cost_generated': i,
    #                         #     # 'reservation_id': self.id,
    #                         # }
    #                         # self.env['fleet.vehicle.log.contract'].create(vals)
    #         else:
    #             raise ValidationError(f'Please enter value greater than KM Out')

    def chauffeur_in_action(self):
        for rec in self:
            res = self.env['rental.progress'].browse(self.env.context.get('active_id'))
            if rec.km_in > res.km_out:
                res.km_in = rec.km_in
                res.time_in = rec.time_in
                res.toll = rec.toll
                res.allowa = rec.allowa
                res.m_tag = rec.m_tag
                res.damage_charges = rec.damage_charges
                res.note = rec.note
                toll_allowance = rec.toll + rec.allowa + rec.m_tag + rec.damage_charges
                res.driven = rec.km_in - res.km_out
                print("current driven" , res.driven)
                res.state = 'chauffeur_in'
                total_days = (rec.time_in - res.time_out)
                if total_days:
                    # year = int(total_days / 365)
                    # month = int((total_days - (year * 365)) / 30)
                    # week = int((total_days - (year * 365)) - month * 30) // 7
                    # day = int((total_days - (year * 365)) - month * 30 - week * 7)
                    record = self.env['res.contract'].search(
                        [('partner_id', '=', res.name.id),
                         ('state', '=', 'confirm')])
                    i = 0
                    td = str(total_days).split(',')
                    td = td[-1].replace(' ', '')
                    hours = datetime.strptime(str(td), "%H:%M:%S").hour
                    minutes = datetime.strptime(str(td), "%H:%M:%S").minute
                    extra_km_rate = 0
                    extra_hour_rate = 0
                    for j in record.contract_lines_id:
                        if j.model_id.name == res.vehicle_no.model_id.name and j.model_id.model_year == res.vehicle_no.model_id.model_year and j.model_id.power_cc == res.vehicle_no.model_id.power_cc:
                            if res.based_on == 'time_and_mileage':
                                total_hours = ((total_days.days * 24) + (total_days.seconds / 3600))
                                res.hours = total_hours
                                res.per_hour_rate = j.per_hour_rate
                                res.hours_value = res.hours * res.per_hour_rate
                                res.km_rate = j.per_km_rate
                                res.km_value = res.driven * res.km_rate
                                res.total_rate = res.hours_value + res.km_value
                                overtime = res.hours - record.apply_over_time
                                if overtime > 0:
                                    res.over_time = True
                                    res.apply_over_time = record.apply_over_time
                                    res.over_time_rate = j.over_time
                                    res.over_time_value = overtime * j.over_time
                                else:
                                    res.over_time = False
                                    res.apply_over_time = 0
                                    res.over_time_rate = 0
                                    res.over_time_value = 0
                                res.apply_out_station = record.apply_out_station
                                if res.apply_out_station <= res.driven:
                                    res.out_of_station = True
                                    res.out_station_rate = j.out_station
                                    res.out_of_station_value = res.out_station_rate
                                    res.net_amount = res.total_rate + res.out_of_station_value + toll_allowance + res.over_time_value
                                else:
                                    res.out_of_station = False
                                    res.net_amount = res.total_rate + toll_allowance + res.over_time_value
                                    res.out_station_rate = 0
                                    res.out_of_station_value = 0
                            elif res.based_on == 'daily':
                                total_hours = ((total_days.days * 24) + (total_days.seconds / 3600))
                                if minutes > 0:
                                    res.hours = total_hours + 1
                                    # res.per_hour_rate = j.per_hour_rate
                                else:
                                    res.hours = total_hours
                                    # res.per_hour_rate = j.per_hour_rate
                                res.days = total_days.days
                                if res.days > 0:
                                    res.day_rate = j.per_day_rate
                                else:
                                    res.day_rate = 0
                                # res.hours_value = res.hours * res.per_hour_rate
                                res.days_value = res.days * res.day_rate
                                extra_km = res.driven - record.km_daily_limit
                                extra_hour = total_hours - record.hourly_daily_limit
                                if extra_km > 0:
                                    res.extra_daily_km = extra_km
                                    res.extra_daily_km_rate = record.addit_daily_km_rate
                                    extra_km_rate = res.extra_daily_km * res.extra_daily_km_rate
                                if extra_hour > 0:
                                    if minutes > 0:
                                        res.extra_daily_hour_rate = record.addit_daily_hour_rate
                                        res.extra_daily_hour = extra_hour + 1
                                        extra_hour_rate = res.extra_daily_hour * res.extra_daily_hour_rate
                                    else:
                                        res.extra_daily_hour_rate = record.addit_daily_hour_rate
                                        res.extra_daily_hour = extra_hour
                                        extra_hour_rate = res.extra_daily_hour * res.extra_daily_hour_rate
                                res.total_rate = res.days_value + extra_km_rate + extra_hour_rate
                                overtime = total_hours - record.apply_over_time
                                if overtime > 0:
                                    res.over_time = True
                                    res.apply_over_time = record.apply_over_time
                                    res.over_time_rate = j.over_time
                                    res.over_time_value = overtime * j.over_time
                                else:
                                    res.over_time = False
                                    res.apply_over_time = 0
                                    res.over_time_rate = 0
                                    res.over_time_value = 0
                                res.apply_out_station = record.apply_out_station
                                if res.apply_out_station <= res.driven:
                                    res.out_of_station = True
                                    res.out_station_rate = j.out_station
                                    res.out_of_station_value = res.out_station_rate
                                    res.net_amount = res.total_rate + res.out_of_station_value + toll_allowance + res.over_time_value
                                else:
                                    res.out_of_station = False
                                    res.net_amount = res.total_rate + toll_allowance + res.over_time_value
                                    res.out_station_rate = 0
                                    res.out_of_station_value = 0
                            elif res.based_on == 'weekly':
                                week = int(total_days.days // 7)
                                day = int(total_days.days - week * 7)
                                if minutes > 0:
                                    res.hours = hours + 1
                                    res.per_hour_rate = j.per_hour_rate
                                else:
                                    res.hours = hours
                                    res.per_hour_rate = j.per_hour_rate
                                res.days = day
                                if res.days > 0:
                                    res.day_rate = j.per_day_rate
                                else:
                                    res.day_rate = 0
                                res.weeks = week
                                if res.weeks > 0:
                                    res.week_rate = j.per_week_rate
                                else:
                                    res.week_rate = 0
                                res.hours_value = res.hours * res.per_hour_rate
                                res.days_value = res.days * res.day_rate
                                res.weeks_value = res.weeks * res.week_rate
                                res.total_rate = (res.hours_value + res.days_value + res.weeks_value)
                                overtime = res.hours - record.apply_over_time
                                if overtime > 0:
                                    res.over_time = True
                                    res.apply_over_time = record.apply_over_time
                                    res.over_time_rate = j.over_time
                                    res.over_time_value = overtime * j.over_time
                                else:
                                    res.over_time = False
                                    res.apply_over_time = 0
                                    res.over_time_rate = 0
                                    res.over_time_value = 0
                                res.apply_out_station = record.apply_out_station
                                if res.apply_out_station <= res.driven:
                                    res.out_of_station = True
                                    res.out_station_rate = j.out_station
                                    res.out_of_station_value = res.out_station_rate
                                    res.net_amount = res.total_rate + res.out_of_station_value + toll_allowance + res.over_time_value
                                else:
                                    res.out_of_station = False
                                    res.net_amount = res.total_rate + toll_allowance + + res.over_time_value
                                    res.out_station_rate = 0
                                    res.out_of_station_value = 0
                            elif res.based_on == 'monthly':
                                month = int(total_days.days / 30)
                                week = int(total_days.days - month * 30) // 7
                                day = int(total_days.days - month * 30 - week * 7)
                                if minutes > 0:
                                    res.hours = hours + 1
                                    res.per_hour_rate = j.per_hour_rate
                                else:
                                    res.hours = hours
                                    res.per_hour_rate = j.per_hour_rate
                                res.days = day
                                if res.days > 0:
                                    res.day_rate = j.per_day_rate
                                else:
                                    res.day_rate = 0
                                res.weeks = week
                                if res.weeks > 0:
                                    res.week_rate = j.per_week_rate
                                else:
                                    res.week_rate = 0
                                res.months = month
                                if res.months > 0:
                                    res.month_rate = j.per_month_rate
                                else:
                                    res.month_rate = 0
                                res.hours_value = res.hours * res.per_hour_rate
                                res.days_value = res.days * res.day_rate
                                res.weeks_value = res.weeks * res.week_rate
                                res.mobil_oil_rate = j.mobil_oil_rate
                                res.oil_filter_rate = j.oil_filter_rate
                                res.air_filter_rate = j.air_filter_rate
                                res.month_value = (res.months * res.month_rate)
                                res.total_rate = res.hours_value + res.days_value + res.weeks_value + res.month_value + res.mobil_oil_rate + res.oil_filter_rate + res.air_filter_rate
                                overtime = res.hours - record.apply_over_time
                                if overtime > 0:
                                    res.over_time = True
                                    res.apply_over_time = record.apply_over_time
                                    res.over_time_rate = j.over_time
                                    res.over_time_value = overtime * j.over_time
                                else:
                                    res.over_time = False
                                    res.apply_over_time = 0
                                    res.over_time_rate = 0
                                    res.over_time_value = 0
                                res.apply_out_station = record.apply_out_station
                                if res.apply_out_station <= res.driven:
                                    res.out_of_station = True
                                    res.out_station_rate = j.out_station
                                    res.out_of_station_value = res.out_station_rate
                                    res.net_amount = res.total_rate + res.out_of_station_value + toll_allowance + res.over_time_value
                                else:
                                    res.out_of_station = False
                                    res.net_amount = res.total_rate + toll_allowance + res.over_time_value
                                    res.out_station_rate = 0
                                    res.out_of_station_value = 0
                            elif res.based_on == 'drop_off_duty':
                                res.drop_off_rate = j.drop_off_rate
                                extra_km = res.driven - record.km_limit
                                extra_hour =  hours - record.hourly_limit
                                if extra_km > 0:
                                    res.extra_drop_off_km = extra_km
                                    res.extra_drop_off_km_rate = record.addit_km_rate
                                    extra_km_rate = res.extra_drop_off_km * res.extra_drop_off_km_rate
                                if extra_hour > 0:
                                    if minutes > 0:
                                        res.hours = hours + 1
                                        res.extra_drop_off_hour_rate = record.addit_hour_rate
                                        res.extra_drop_off_hour = extra_hour + 1
                                    else:
                                        res.hours = hours
                                        res.extra_drop_off_hour_rate = record.addit_hour_rate
                                        res.extra_drop_off_hour = extra_hour
                                res.drop_off_value = ((res.extra_drop_off_hour * res.extra_drop_off_km_rate) + res.drop_off_rate + extra_km_rate)
                                res.total_rate = res.drop_off_value
                                res.net_amount = res.total_rate  + toll_allowance
                            elif res.based_on == 'airport_duty':
                                res.airport_duty_rate = j.airport_duty_rate
                                extra_km = res.driven - record.km_airport_limit
                                extra_hour = hours - record.hourly_airport_limit
                                if extra_km > 0:
                                    res.extra_airport_km = extra_km
                                    res.extra_airport_km_rate = record.addit_airport_km_rate
                                    extra_km_rate = res.extra_airport_km * res.extra_airport_km_rate
                                if extra_hour > 0:
                                    if minutes > 0:
                                        res.hours = hours + 1
                                        res.extra_airport_hour_rate = record.addit_airport_hour_rate
                                        res.extra_airport_hour = extra_hour + 1
                                    else:
                                        res.hours = hours
                                        res.extra_airport_hour_rate = record.addit_airport_hour_rate
                                        res.extra_airport_hour = extra_hour
                                res.airport_duty_value = ((res.extra_airport_hour * res.extra_airport_hour_rate) + res.airport_duty_rate + extra_km_rate)
                                res.total_rate = res.airport_duty_value
                                res.net_amount = res.total_rate + toll_allowance
                            elif res.based_on == 'out_station':
                                res.days = total_days.days
                                res.out_station_rate = j.out_station
                                res.out_of_station_value = res.days * res.out_station_rate
                                res.total_rate = res.out_of_station_value
                                res.net_amount = res.total_rate + toll_allowance
                else:
                    res.days = 0
                    res.weeks = 0
                    res.months = 0
                    res.day_rate = 0
                    res.week_rate = 0
                    res.month_rate = 0
                    res.drop_off_rate = 0
            else:
                raise ValidationError(f'Please enter value greater than KM Out')
