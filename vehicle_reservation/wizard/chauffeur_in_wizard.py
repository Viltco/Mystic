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
                toll_allowance = rec.toll + rec.allowa
                driven = rec.km_in - res.km_out
                print("current driven" , driven)
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
                    for j in record.contract_lines_id:
                        if j.model_id.name == res.vehicle_no.model_id.name and j.model_id.model_year == res.vehicle_no.model_id.model_year and j.model_id.power_cc == res.vehicle_no.model_id.power_cc:
                            res.per_hour_rate = j.per_hour_rate
                            if res.based_on == 'daily':
                                if minutes > 0:
                                    res.hours = hours + 1
                                else:
                                    res.hours = hours
                                res.days = total_days.days
                                res.day_rate = j.per_day_rate
                                res.total_rate = (res.days * res.day_rate) + (res.hours * res.per_hour_rate)
                                if res.apply_out_station <= driven:
                                    res.apply_out_station = record.apply_out_station
                                    res.out_of_station = True
                                    res.out_station_rate = j.out_station
                                    res.net_amount = res.total_rate + res.out_station_rate + toll_allowance
                                else:
                                    res.net_amount = res.total_rate + toll_allowance
                                    res.out_station_rate = 0
                            elif res.based_on == 'weekly':
                                week = int(total_days.days // 7)
                                day = int(total_days.days - week * 7)
                                # hours = datetime.strptime(str(total_days).replace(' days', ''), "%d, %H:%M:%S").hour
                                # minutes = datetime.strptime(str(total_days).replace(' days', ''), "%d, %H:%M:%S").minute
                                if minutes > 0:
                                    res.hours = hours + 1
                                else:
                                    res.hours = hours
                                print("Weekly")
                                print(week)
                                print(day)
                                res.days = day
                                res.weeks = week
                                res.day_rate = j.per_day_rate
                                res.week_rate = j.per_week_rate
                                res.total_rate = ((res.days * res.day_rate) + (
                                        res.weeks * res.week_rate) + (res.hours * res.per_hour_rate))
                                if res.apply_out_station <= driven:
                                    print("Out Station")
                                    res.apply_out_station = record.apply_out_station
                                    res.out_of_station = True
                                    res.out_station_rate = j.out_station
                                    res.net_amount = res.total_rate + res.out_station_rate + toll_allowance
                                else:
                                    res.net_amount = res.total_rate + toll_allowance
                                    res.out_station_rate = 0
                            elif res.based_on == 'monthly':
                                month = int(total_days.days / 30)
                                week = int(total_days.days - month * 30) // 7
                                day = int(total_days.days - month * 30 - week * 7)
                                # td = str(total_days).split(',')
                                # td = td[-1].replace(' ', '')
                                print(td)
                                print("hours", type(hours))
                                print("month", month)
                                print("week", week)
                                print("day", day)
                                print("minute", minutes)
                                if minutes > 0:
                                    print("True")
                                    res.hours = hours + 1
                                else:
                                    res.hours = hours
                                print("monthly")
                                res.days = day
                                res.weeks = week
                                res.months = month
                                res.day_rate = j.per_day_rate
                                res.week_rate = j.per_week_rate
                                res.month_rate = j.per_month_rate
                                print("Total month", res.months)
                                print("Total week", res.weeks)
                                print("Total day", res.days)
                                print("Rate month", res.month_rate)
                                print("Rate week", res.week_rate)
                                print("Rate day", res.day_rate)
                                print("Driven", res.driven)
                                res.total_rate = ((res.days * res.day_rate) + (res.weeks * res.week_rate) + (
                                        res.months * res.month_rate) + (res.hours * res.per_hour_rate))
                                if res.apply_out_station <= driven:
                                    print("Out Station")
                                    res.apply_out_station = record.apply_out_station
                                    res.out_of_station = True
                                    res.out_station_rate = j.out_station
                                    res.net_amount = res.total_rate + res.out_station_rate + toll_allowance
                                else:
                                    res.net_amount = res.total_rate + toll_allowance
                                    res.out_station_rate = 0
                            elif res.based_on == 'airport':
                                print("hours", hours)
                                print("minute", minutes)
                                res.airport_rate = j.airport_rate
                                extra_km = driven - record.km_limit
                                print("Extra kmmm", extra_km)
                                extra_hour =  hours - record.hourly_limit
                                print("Extra ho", extra_hour)
                                if extra_km > 0:
                                    print("Extra KM", extra_km)
                                    res.extra_airport_km = extra_km
                                    extra_km_rate = extra_km * record.addit_km_rate
                                    res.total_rate = (
                                                (res.days * res.day_rate) + (res.weeks * res.week_rate) + (res.months * res.month_rate) + res.airport_rate + extra_km_rate)
                                elif extra_hour > 0:
                                    print("Extra Hour", extra_hour)
                                    if minutes > 0:
                                        res.hours = extra_hour + 1
                                        res.per_hour_rate = record.addit_hour_rate
                                    else:
                                        res.hours = extra_hour
                                        res.per_hour_rate = record.addit_hour_rate
                                    print("True")
                                    res.total_rate = (
                                                (res.days * res.day_rate) + (res.weeks * res.week_rate) + (
                                                res.months * res.month_rate) + res.airport_rate + (
                                                            res.hours * res.per_hour_rate) + extra_km_rate)
                                res.net_amount = res.total_rate
                else:
                    res.days = 0
                    res.weeks = 0
                    res.months = 0
                    res.day_rate = 0
                    res.week_rate = 0
                    res.month_rate = 0
                    res.airport_rate = 0
            else:
                raise ValidationError(f'Please enter value greater than KM Out')
