from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from datetime import date


class RentalProgress(models.Model):
    _name = "rental.progress"
    _description = "Rental Progress"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'rental_seq'

    rental_seq = fields.Char(string='Rental', copy=False, readonly=True, default='New')
    name = fields.Many2one('res.partner', string="Customer", tracking=True)
    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True, required=True)
    vehicle_no = fields.Many2one('fleet.vehicle', string="Vehicle", tracking=True)
    driver_id = fields.Many2one('res.partner', string="Driver", tracking=True,
                                domain=[('partner_type', '=', 'is_driver')])
    odometer = fields.Integer(compute='_get_odometer', string='Current Meter Reading',
                              help='Odometer measure of the vehicle at the moment of this log')
    source = fields.Many2one('vehicle.reservation', string="Source", tracking=True)
    rentee_type = fields.Selection([
        ('mr', 'MR.'),
        ('mrs', 'MRS.'),
        ('prof', 'Prof.'),
        ('dr', 'Dr.'),
    ], default='mr', string="Rentee Name")
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    based_on = fields.Selection([
        ('time_and_mileage', 'Time And Mileage'),
        ('drop_off_duty', 'Drop Off Duty'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),('airport_duty', 'Airport Transfer') ,('out_station', 'Out Station')], default='time_and_mileage', string="Based On")
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit', 'Credit')], default='cash', string="Payment Type")
    mobile = fields.Char(string="Mobile", tracking=True, related='name.mobile')
    km_in = fields.Integer(string="Kms In", tracking=True)
    km_out = fields.Integer(string="Kms Out", tracking=True)
    toll = fields.Integer(string="Toll", tracking=True)
    allowa = fields.Integer(string="Allowa.", tracking=True)
    m_tag = fields.Integer(string="M-Tag", tracking=True)
    damage_charges = fields.Integer(string="Damage Charges (Depreciation)", tracking=True)

    time_in = fields.Datetime('Time In')
    time_out = fields.Datetime('Time Out')
    note = fields.Text(string='Note')
    out_of_station = fields.Boolean(default=False)
    over_night = fields.Boolean(default=False)
    over_time = fields.Boolean(default=False)
    button_show = fields.Boolean(default=False)

    hours = fields.Integer(string='Hours')
    per_hour_rate = fields.Integer(string='Hour Rate')
    days = fields.Integer(string='Days')
    day_rate = fields.Integer(string='Day Rate')
    weeks = fields.Integer(string='Weeks')
    week_rate = fields.Integer(string='Week Rate')
    months = fields.Integer(string='Months')
    month_rate = fields.Integer(string='Month Rate')
    mobil_oil_rate = fields.Float(string='Mobil Oil Rate')
    oil_filter_rate = fields.Float(string='Oil Filter Rate')
    air_filter_rate = fields.Float(string='Air Filter Rate')
    drop_off_rate = fields.Integer(string='Drop Off Duty Rate')
    extra_drop_off_km = fields.Integer(string='Extra KMs(Drop Off Duty)')
    extra_drop_off_km_rate = fields.Integer(string='Extra KM Rate(Drop Off Duty)')
    extra_drop_off_hour = fields.Integer(string='Extra Hours(Drop Off Duty)')
    extra_drop_off_hour_rate = fields.Integer(string='Extra Hour Rate(Drop Off Duty)')
    airport_duty_rate = fields.Integer(string='Airport Duty Rate')
    extra_airport_km_rate = fields.Integer(string='Extra KM Rate(Airport Duty)')
    extra_airport_km = fields.Integer(string='Extra KMs(Airport Duty)')
    extra_airport_hour_rate = fields.Integer(string='Extra Hour Rate(Airport Duty)')
    extra_airport_hour = fields.Integer(string='Extra Hours(Airport Duty)')

    hours_value = fields.Integer(string='Hours Value')
    days_value = fields.Integer(string='Days Value')
    weeks_value = fields.Integer(string='Weeks Value')
    month_value = fields.Integer(string='Monthly Value')
    drop_off_value = fields.Integer(string='Drop Off Duty Value')
    airport_duty_value = fields.Integer(string='Airport Duty Value')
    km_value = fields.Integer(string='KM Value')
    km_rate = fields.Integer(string='KM Rate')
    over_time_value = fields.Integer(string='Over Time Value')
    out_of_station_value = fields.Integer(string='Out of Station Value')

    total_rate = fields.Integer(string='Total Rate')
    driven = fields.Integer(string="Driven", tracking=True)
    # , compute="_compute_driven"
    apply_out_station = fields.Integer(string='Apply Out Station After')
    out_station_rate = fields.Integer(string='Out Station Rate')
    apply_over_time = fields.Integer(string='Apply Over Time After')
    over_time_rate = fields.Integer(string='Over Time Rate')
    net_amount = fields.Integer(string='Net Amount')

    state = fields.Selection(
        [('ready_for_departure', 'Ready For Departure'), ('chauffeur_out', 'Chauffeur Out'),
         ('chauffeur_in', 'Chauffeur In'),
         ('rental_close', 'Rental Closed') , ('cancel', 'Cancelled')],
        default='ready_for_departure',
        string="Status", tracking=True)
    reservation_id = fields.Many2one('vehicle.reservation')
    stage_id = fields.Selection([
        ('billed', 'BILLED'),
        ('not_billed', 'NOT BILLED')], default='not_billed', string="Stage ID")
    pickup = fields.Text(string='Pickup')
    program = fields.Text(string='Program')

    # @api.onchange('toll', 'allowa', 'net_amount')
    # def _onchange_net_amount(self):
    #     print("Before Plus",self.net_amount)
    #     a = self.net_amount
    #     self.net_amount = a + self.toll + self.allowa
    #     print("After Plus",self.net_amount)

    @api.onchange('out_of_station')
    def _onchange_out_station(self):
        if self.out_of_station:
            record = self.env['res.contract'].search(
                [('partner_id', '=', self.name.id),
                 ('state', '=', 'confirm')])
            overtime = self.hours - record.apply_over_time
            over_rate = 0
            toll_allowance = self.toll + self.allowa + self.damage_charges + self.m_tag
            for j in record.contract_lines_id:
                if j.model_id.name == self.vehicle_no.model_id.name and j.model_id.model_year == self.vehicle_no.model_id.model_year and j.model_id.power_cc == self.vehicle_no.model_id.power_cc:
                    # if self.out_of_station:
                    print("out station before")
                    print(self.apply_out_station)
                    print(self.driven)
                    if overtime > 0:
                        self.over_time = True
                        self.apply_over_time = record.apply_over_time
                        self.over_time_rate = j.over_time
                        over_rate = overtime * self.over_time_rate
                    if self.apply_out_station <= self.driven:
                        print("out station done")
                        self.out_station_rate = j.out_station
                        self.net_amount = self.total_rate + self.out_station_rate + over_rate + toll_allowance
        else:
            self.net_amount = self.net_amount - self.out_station_rate

    @api.onchange('over_time')
    def _onchange_over_time(self):
        if self.over_time:
            record = self.env['res.contract'].search(
                [('partner_id', '=', self.name.id),
                 ('state', '=', 'confirm')])
            overtime = self.hours - record.apply_over_time
            print("overtime" , overtime)
            out_station = 0
            toll_allowance = self.toll + self.allowa + self.damage_charges + self.m_tag
            for j in record.contract_lines_id:
                if j.model_id.name == self.vehicle_no.model_id.name and j.model_id.model_year == self.vehicle_no.model_id.model_year and j.model_id.power_cc == self.vehicle_no.model_id.power_cc:
                    print("true")
                    if self.apply_out_station <= self.driven:
                        self.out_of_station = True
                        print("out station done")
                        self.out_station_rate = j.out_station
                        out_station = self.out_station_rate
                    if overtime > 0:
                        print("viltco")
                        self.over_time = True
                        self.apply_over_time = record.apply_over_time
                        self.over_time_rate = j.over_time
                        # over_rate = overtime * self.over_time_rate
                        self.net_amount = self.total_rate + out_station + (overtime * self.over_time_rate) + toll_allowance
        else:
            record = self.env['res.contract'].search(
                [('partner_id', '=', self.name.id),
                 ('state', '=', 'confirm')])
            self.net_amount = self.net_amount - ((self.hours - record.apply_over_time) * self.over_time_rate)

    @api.onchange('time_in', 'time_out')
    def _onchange_calculate_dwm(self):
        if self.time_out and self.time_in:
            total_days = (self.time_in - self.time_out)
            print("total days" , total_days)
            if total_days:
                record = self.env['res.contract'].search(
                    [('partner_id', '=', self.name.id),
                     ('state', '=', 'confirm')])
                i = 0
                td = str(total_days).split(',')
                td = td[-1].replace(' ', '')
                hours = datetime.strptime(str(td), "%H:%M:%S").hour
                print("hour" , hours)
                minutes = datetime.strptime(str(td), "%H:%M:%S").minute
                print("minute" , minutes)
                overtime = self.hours - record.apply_over_time
                print("over time" , overtime)
                self.driven = self.km_in - self.km_out
                toll_allowance = self.toll + self.allowa + self.damage_charges + self.m_tag
                extra_km_rate = 0
                total_hours = 0
                for j in record.contract_lines_id:
                    if j.model_id.name == self.vehicle_no.model_id.name and j.model_id.model_year == self.vehicle_no.model_id.model_year and j.model_id.power_cc == self.vehicle_no.model_id.power_cc:
                        # self.per_hour_rate = j.per_hour_rate
                        if self.based_on == 'time_and_mileage':
                            total_hours = ((total_days.days * 24) + (total_days.seconds / 3600))
                            print("total_hours" , total_hours)
                            if minutes > 0:
                                self.hours = total_hours + 1
                                self.per_hour_rate = j.per_hour_rate
                            else:
                                self.hours = total_hours
                                self.per_hour_rate = j.per_hour_rate

                            # self.hours = hours
                            # self.per_hour_rate = j.per_hour_rate
                            self.hours_value = self.hours * self.per_hour_rate
                            self.km_rate = j.per_km_rate
                            self.km_value = self.driven * self.km_rate
                            self.total_rate = self.hours_value + self.km_value
                            self.apply_out_station = record.apply_out_station
                            if self.apply_out_station <= self.driven:
                                self.out_of_station = True
                                self.out_station_rate = j.out_station
                                self.out_of_station_value = self.out_station_rate
                                self.net_amount = self.total_rate + self.out_of_station_value + toll_allowance
                            else:
                                self.out_of_station = False
                                self.net_amount = self.total_rate + toll_allowance
                                self.out_station_rate = 0
                        elif self.based_on == 'daily':
                            if minutes > 0:
                                self.hours = hours + 1
                                self.per_hour_rate = j.per_hour_rate
                            else:
                                self.hours = hours
                                self.per_hour_rate = j.per_hour_rate
                            self.days = total_days.days
                            if self.days > 0:
                                self.day_rate = j.per_day_rate
                            else:
                                self.day_rate = 0
                            self.hours_value = self.hours * self.per_hour_rate
                            self.days_value = self.days * self.day_rate
                            self.total_rate = self.days_value + self.hours_value
                            if overtime > 0:
                                self.over_time = True
                                self.apply_over_time = record.apply_over_time
                                self.over_time_rate = j.over_time
                                self.over_time_value = overtime * j.over_time
                            else:
                                self.over_time = False
                                self.apply_over_time = 0
                                self.over_time_rate = 0
                                self.over_time_value = 0
                            self.apply_out_station = record.apply_out_station
                            if self.apply_out_station <= self.driven:
                                self.out_of_station = True
                                self.out_station_rate = j.out_station
                                self.out_of_station_value = self.out_station_rate
                                self.net_amount = self.total_rate + self.out_of_station_value + toll_allowance
                            else:
                                self.out_of_station = False
                                self.net_amount = self.total_rate + toll_allowance + self.over_time_value
                                self.out_station_rate = 0
                        elif self.based_on == 'weekly':
                            week = int(total_days.days // 7)
                            day = int(total_days.days - week * 7)
                            # if 0 < minutes < 15:
                            #     self.hours = hours + 1
                            #     self.per_hour_rate = j.per_hour_rate
                            # elif 15 < minutes < 30:
                            #
                            # elif 30 < minutes < 45:
                            #
                            # elif 45 < minutes < 60:
                            #
                            # else:
                            #     self.hours = hours
                            #     self.per_hour_rate = j.per_hour_rate
                            if minutes > 0:
                                self.hours = hours + 1
                                self.per_hour_rate = j.per_hour_rate
                            else:
                                self.hours = hours
                                self.per_hour_rate = j.per_hour_rate
                            self.days = day
                            if self.days > 0:
                                self.day_rate = j.per_day_rate
                            else:
                                self.day_rate = 0
                            self.weeks = week
                            if self.weeks > 0:
                                self.week_rate = j.per_week_rate
                            else:
                                self.week_rate = 0
                            self.hours_value = self.hours * self.per_hour_rate
                            self.days_value = self.days * self.day_rate
                            self.weeks_value = self.weeks * self.week_rate
                            self.total_rate = self.hours_value + self.days_value + self.weeks_value
                            if overtime > 0:
                                self.over_time = True
                                self.apply_over_time = record.apply_over_time
                                self.over_time_rate = j.over_time
                                self.over_time_value = overtime * j.over_time
                            else:
                                self.over_time = False
                                self.apply_over_time = 0
                                self.over_time_rate = 0
                                self.over_time_value = 0
                            self.apply_out_station = record.apply_out_station
                            if self.apply_out_station <= self.driven:
                                self.out_of_station = True
                                self.out_station_rate = j.out_station
                                self.out_of_station_value = self.out_station_rate
                                self.net_amount = self.total_rate + self.out_of_station_value + toll_allowance
                            else:
                                self.out_of_station = False
                                self.net_amount = self.total_rate + toll_allowance + self.over_time_value
                                self.out_station_rate = 0
                        elif self.based_on == 'monthly':
                            month = int(total_days.days / 30)
                            week = int(total_days.days - month * 30) // 7
                            day = int(total_days.days - month * 30 - week * 7)
                            if minutes > 0:
                                self.hours = hours + 1
                                self.per_hour_rate = j.per_hour_rate
                            else:
                                self.hours = hours
                                self.per_hour_rate = j.per_hour_rate
                            self.days = day
                            if self.days > 0:
                                self.day_rate = j.per_day_rate
                            else:
                                self.day_rate = 0
                            self.weeks = week
                            if self.weeks > 0:
                                self.week_rate = j.per_week_rate
                            else:
                                self.week_rate = 0
                            self.months = month

                            if self.months > 0:
                                self.month_rate = j.per_month_rate
                            else:
                                self.month_rate = 0
                            self.hours_value = self.hours * self.per_hour_rate
                            self.days_value = self.days * self.day_rate
                            self.weeks_value = self.weeks * self.week_rate
                            self.mobil_oil_rate = j.mobil_oil_rate
                            self.oil_filter_rate = j.oil_filter_rate
                            self.air_filter_rate = j.air_filter_rate
                            self.month_value = (self.months * self.month_rate)
                            self.total_rate = self.hours_value + self.days_value + self.weeks_value + self.month_value + self.mobil_oil_rate + self.oil_filter_rate + self.air_filter_rate
                            if overtime > 0:
                                self.over_time = True
                                self.apply_over_time = record.apply_over_time
                                self.over_time_rate = j.over_time
                                self.over_time_value = overtime * j.over_time
                            else:
                                self.over_time = False
                                self.apply_over_time = 0
                                self.over_time_rate = 0
                                self.over_time_value = 0
                            self.apply_out_station = record.apply_out_station
                            if self.apply_out_station <= self.driven:
                                self.out_of_station = True
                                self.out_station_rate = j.out_station
                                self.out_of_station_value = self.out_station_rate
                                self.net_amount = self.total_rate + self.out_of_station_value + toll_allowance
                            else:
                                self.out_of_station = False
                                self.net_amount = self.total_rate + toll_allowance + self.over_time_value
                                self.out_station_rate = 0
                        elif self.based_on == 'drop_off_duty':
                            self.drop_off_rate = j.drop_off_rate
                            extra_km = self.driven - record.km_limit
                            extra_hour = hours - record.hourly_limit
                            if extra_km > 0:
                                self.extra_drop_off_km = extra_km
                                self.extra_drop_off_km_rate = record.addit_km_rate
                                extra_km_rate = self.extra_drop_off_km * self.extra_drop_off_km_rate
                            if extra_hour > 0:
                                if minutes > 0:
                                    self.hours = hours + 1
                                    self.extra_drop_off_hour_rate = record.addit_hour_rate
                                    self.extra_drop_off_hour = extra_hour + 1
                                else:
                                    self.hours = hours
                                    self.extra_drop_off_hour_rate = record.addit_hour_rate
                                    self.extra_drop_off_hour = extra_hour
                            self.drop_off_value = ((self.extra_drop_off_hour * self.extra_drop_off_km_rate) + self.drop_off_rate + extra_km_rate)
                            self.total_rate = self.drop_off_value
                            self.net_amount = self.total_rate
                        elif self.based_on == 'airport_duty':
                            self.airport_duty_rate = j.airport_duty_rate
                            extra_km = self.driven - record.km_airport_limit
                            extra_hour = hours - record.hourly_airport_limit
                            if extra_km > 0:
                                self.extra_airport_km = extra_km
                                self.extra_airport_km_rate = record.addit_airport_km_rate
                                extra_km_rate = self.extra_airport_km * self.extra_airport_km_rate
                            if extra_hour > 0:
                                if minutes > 0:
                                    self.hours = hours + 1
                                    self.extra_airport_hour_rate = record.addit_airport_hour_rate
                                    self.extra_airport_hour = extra_hour + 1
                                else:
                                    self.hours = hours
                                    self.extra_airport_hour_rate = record.addit_airport_hour_rate
                                    self.extra_airport_hour = extra_hour
                            self.airport_duty_value = ((self.extra_airport_hour * self.extra_airport_hour_rate) + self.airport_duty_rate + extra_km_rate)
                            self.total_rate = self.airport_duty_value
                            self.net_amount = self.total_rate
                        elif self.based_on == 'out_station':
                            self.days = total_days.days
                            self.out_station_rate = j.out_station
                            self.out_of_station_value = self.days * self.out_station_rate
                            self.total_rate = self.out_of_station_value
                            self.net_amount = self.total_rate + toll_allowance

                    # else:
                    #     self.days = 0
                    #     self.weeks = 0
                    #     self.months = 0
                    #     self.day_rate = 0
                    #     self.week_rate = 0
                    #     self.month_rate = 0
            else:
                self.days = 0
                self.weeks = 0
                self.months = 0
                self.day_rate = 0
                self.week_rate = 0
                self.month_rate = 0
                self.drop_off_rate = 0
        else:
            self.days = 0
            self.weeks = 0
            self.months = 0
            self.day_rate = 0
            self.week_rate = 0
            self.month_rate = 0
            self.drop_off_rate = 0

    @api.model
    def create(self, values):
        if 'branch_id' in values:
            seq = self.env['ir.sequence'].search(
                [('name', '=', 'Rental'), ('branch_id', '=', values['branch_id'])])
            self.env['ir.sequence'].next_by_code(seq.code)
            values['rental_seq'] = seq.prefix + '-' + seq.branch_id.code + '-' + str(seq.number_next_actual) or _('New')
        return super(RentalProgress, self).create(values)

    def _get_odometer(self):
        FleetVehicalOdometer = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = FleetVehicalOdometer.search([('vehicle_id', '=', record.vehicle_no.id)], limit=1,
                                                           order='value desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    def action_chauffeur_out(self):
        return {
            'name': _('Chauffeur Out'),
            'res_model': 'chauffeur.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'rental.progress',
                'active_ids': self.ids,
                'default_odometer': self.odometer,
                'default_km_out': self.odometer,
                'default_time_out': self.time_out,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_chauffeur_in(self):
        return {
            'name': _('Chauffeur In'),
            'res_model': 'chauffeur.in',
            'view_mode': 'form',
            'context': {
                'active_model': 'rental.progress',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window', }

    def action_rental_closed(self):
        for rec in self:
            record = self.env['fleet.vehicle.odometer'].search([('vehicle_id', '=', rec.vehicle_no.id)],
                                                               order='value desc', limit=1)
            l = record.value
            vals = {
                'date': rec.time_in,
                'vehicle_id': rec.vehicle_no.id,
                'driver_id': rec.driver_id,
                'driven': rec.driven,
                'value': l + rec.driven
            }
            result = rec.env['fleet.vehicle.state'].search([('sequence', '=', 0)])
            for i in result:
                rec.vehicle_no.state_id = i.id
            rec.env['fleet.vehicle.odometer'].create(vals)
            res = self.env['fleet.vehicle.log.contract'].search([('vehicle_id', '=', rec.vehicle_no.id)])
            for r in res:
                r.write({
                    'state': 'closed'
                })
            rec.state = 'rental_close'

    @api.onchange('km_in', 'km_out', 'driven')
    def _onchange_driven(self):
        for rec in self:
            rec.driven = rec.km_in - rec.km_out

    def action_create_invoice(self):
        for rec in self:
            line_vals = []
            rental_vals = []
            if rec.hours_value > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    service = self.env['service.lines'].search([('service_type' ,'=','hour')])
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.hours_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    service = self.env['service.lines'].search([('service_type', '=', 'hour')])
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.hours_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    service = self.env['service.lines'].search([('service_type', '=', 'hour')])
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.hours_value,
                    }))
            if rec.days_value > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','daily')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.days_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'daily')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.days_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'daily')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.days_value,
                    }))
            if rec.weeks_value > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','weekly')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.weeks_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'weekly')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.weeks_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'weekly')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.weeks_value,
                    }))
            if rec.month_value > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','monthly')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.month_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'monthly')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.month_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'monthly')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.month_value,
                    }))
            if rec.mobil_oil_rate > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','mobil_oil')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.mobil_oil_rate,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'mobil_oil')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.mobil_oil_rate,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'mobil_oil')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.mobil_oil_rate,
                    }))
            if rec.oil_filter_rate > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','oil_filter')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.oil_filter_rate,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'oil_filter')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.oil_filter_rate,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'oil_filter')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.oil_filter_rate,
                    }))
            if rec.air_filter_rate > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','air_filter')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.air_filter_rate,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'air_filter')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.air_filter_rate,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'air_filter')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.air_filter_rate,
                    }))
            if rec.km_value > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','km')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.km_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'km')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.km_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'km')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.km_value,
                    }))
            if rec.drop_off_value > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','drop_off_duty')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.drop_off_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'drop_off_duty')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.drop_off_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'drop_off_duty')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.drop_off_value,
                    }))
            if rec.over_time_value > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','over_time')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.over_time_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'over_time')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.over_time_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'over_time')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.over_time_value,
                    }))
            if rec.out_of_station_value > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','out_station')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.out_of_station_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'out_station')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.out_of_station_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'out_station')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.out_station_rate,
                    }))
            if rec.airport_duty_value > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','airport_duty')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.airport_duty_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'airport_duty')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.airport_duty_value,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'airport_duty')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.airport_duty_value,
                    }))
            if rec.toll > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','toll')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.toll,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'toll')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.toll,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'toll')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.toll,
                    }))
            if rec.allowa > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','allowa')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.allowa,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'allowa')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.allowa,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'allowa')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.allowa,
                    }))
            if rec.m_tag > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','m_tag')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.m_tag,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'm_tag')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.m_tag,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'm_tag')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.m_tag,
                    }))
            if rec.damage_charges > 0:
                if rec.vehicle_no.booleans == 'pool_id':
                    print("pool")
                    service = self.env['service.lines'].search([('service_type' ,'=','damage_charges')])
                    print("service" ,service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.damage_charges,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool':
                    print("Non pool")
                    service = self.env['service.lines'].search([('service_type', '=', 'damage_charges')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.damage_charges,
                    }))
                elif rec.vehicle_no.booleans == 'non_pool_other':
                    print("Non pool Other")
                    service = self.env['service.lines'].search([('service_type', '=', 'damage_charges')])
                    print("service", service.pool_id.name)
                    line_vals.append((0, 0, {
                        'product_id': service.non_pool_other_id.id,
                        'analytic_account_id': rec.vehicle_no.analytical_account_id.id,
                        'date_rental': rec.time_out,
                        'rental_id': rec.id,
                        'rentee_name': rec.first_name + '' + rec.last_name,
                        'price_unit': rec.damage_charges,
                    }))
            print(line_vals)
            print("lines" , line_vals[0])
            print("lines after" , line_vals[0][-1]['rental_id'])
            # rental = line_vals[0][-1]['rental_id']
            # if rental == rec.rental_id.id:

            result = sum(item[-1]['price_unit'] for item in line_vals)
            print(result)
            rental_vals.append((0, 0, {
                'date_rental': rec.create_date.date(),
                'rental_id': rec.id,
                # 'description': r.time_out,
                'rentee_name': rec.first_name + '' + rec.last_name,
                'amount': result,
            }))
            r = self.env['account.journal'].search([('branch_id', '=', rec.branch_id.id), ('type', '=', 'sale')])
            print(r)
            invoice = {
                'invoice_line_ids': line_vals,
                'rental_lines_id': rental_vals,
                'partner_id': rec.name.id,
                'invoice_date': date.today(),
                'branch_id': rec.branch_id.id,
                'journal_id': r.id,
                'fiscal_position_id': rec.branch_id.fiscal_position_id.id,
                'rental': rec.ids,
                'move_type': 'out_invoice',
            }
            self.stage_id = 'billed'
            self.button_show = True
            record = self.env['account.move'].create(invoice)

    def action_server_invoice(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['rental.progress'].browse(selected_ids)
        if len(selected_records) <= 1:
            raise ValidationError("Please select multiple Rentals to merge in the list view.... ")
        child_vals = []
        for rental_id in selected_records:
            child_vals.append(rental_id.name)
            if selected_records.name == rental_id.name:
                if rental_id.stage_id == 'not_billed':
                    print('name matched')
                    if selected_records.branch_id.name == rental_id.branch_id.name:
                        merge = True
                    else:
                        raise ValidationError("Branches are Different")
                else:
                    raise ValidationError("Stages are Different")
            else:
                raise ValidationError("Customers are Different")
                merge = False
                break
        if merge:
            line_vals = []
            rental_vals = []
            j = self.env['account.journal'].search([('branch_id', '=', self.branch_id.id), ('type', '=', 'sale')])
            for r in selected_records:
                rental_vals.append((0, 0, {
                    'date_rental': r.create_date,
                    'rental_id': r.id,
                    # 'description': r.time_out,
                    'rentee_name': r.first_name + '' + r.last_name,
                    'amount': r.net_amount,
                }))
                if r.hours_value > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        service = self.env['service.lines'].search([('service_type', '=', 'hour')])
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.hours_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        service = self.env['service.lines'].search([('service_type', '=', 'hour')])
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.hours_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        service = self.env['service.lines'].search([('service_type', '=', 'hour')])
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.hours_value,
                        }))
                if r.days_value > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        service = self.env['service.lines'].search([('service_type', '=', 'daily')])
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.days_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        service = self.env['service.lines'].search([('service_type', '=', 'daily')])
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.days_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        service = self.env['service.lines'].search([('service_type', '=', 'daily')])
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.days_value,
                        }))
                if r.weeks_value > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'weekly')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.weeks_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'weekly')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.weeks_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'weekly')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.weeks_value,
                        }))
                if r.month_value > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'monthly')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.month_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'monthly')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.month_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'monthly')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.month_value,
                        }))
                if r.mobil_oil_rate > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'mobil_oil')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.mobil_oil_rate,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'mobil_oil')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.mobil_oil_rate,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'mobil_oil')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.mobil_oil_rate,
                        }))
                if r.oil_filter_rate > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'oil_filter')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.oil_filter_rate,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'oil_filter')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.oil_filter_rate,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'oil_filter')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.oil_filter_rate,
                        }))
                if r.air_filter_rate > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'air_filter')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.air_filter_rate,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'air_filter')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.air_filter_rate,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'air_filter')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.air_filter_rate,
                        }))
                if r.km_value > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'km')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.km_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'km')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.km_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'km')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.km_value,
                        }))
                if r.drop_off_value > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'drop_off_duty')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.drop_off_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'drop_off_duty')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.drop_off_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'drop_off_duty')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.drop_off_value,
                        }))
                if r.airport_duty_value > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'airport_duty')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.airport_duty_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'airport_duty')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.airport_duty_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'airport_duty')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.airport_duty_value,
                        }))
                if r.over_time_value > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'over_time')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.over_time_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'over_time')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.over_time_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'over_time')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.over_time_value,
                        }))
                if r.out_of_station_value > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'out_station')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.out_of_station_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'out_station')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.out_of_station_value,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'out_station')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.out_of_station_value,
                        }))
                if r.toll > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'toll')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.toll,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'toll')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.toll,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'toll')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.toll,
                        }))
                if r.allowa > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'allowa')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.allowa,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'allowa')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.allowa,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'allowa')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.allowa,
                        }))
                if r.m_tag > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'm_tag')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.m_tag,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'm_tag')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.m_tag,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'm_tag')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.m_tag,
                        }))
                if r.damage_charges > 0:
                    if r.vehicle_no.booleans == 'pool_id':
                        print("pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'damage_charges')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.damage_charges,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool':
                        print("Non pool")
                        service = self.env['service.lines'].search([('service_type', '=', 'damage_charges')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.damage_charges,
                        }))
                    elif r.vehicle_no.booleans == 'non_pool_other':
                        print("Non pool Other")
                        service = self.env['service.lines'].search([('service_type', '=', 'damage_charges')])
                        print("service", service.pool_id.name)
                        line_vals.append((0, 0, {
                            'product_id': service.non_pool_other_id.id,
                            'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                            'date_rental': r.time_out,
                            'rental_id': r.id,
                            'rentee_name': r.first_name + '' + r.last_name,
                            'price_unit': r.damage_charges,
                        }))
                r.stage_id = 'billed'
                r.button_show = True
            print(line_vals)
            print(rental_vals)
            # print("lines", line_vals[0])
            # print("lines after", line_vals[0][-1]['rental_id'])
            # rental = line_vals[0][-1]['rental_id']
            #
            # # result = sum(item[-1]['price_unit'] for item in line_vals)
            # print("rental",rental)
            # for line in line_vals:
            #     print("after loop",line[-1]['rental_id'])
            #     if rental == line[-1]['rental_id']:
            #         print("after condition" , line)
            #     rental_vals.append((0, 0, {
            #         'date_rental': r.create_date,
            #         'rental_id': r.id,
            #         # 'description': r.time_out,
            #         'rentee_name': r.first_name + '' + r.last_name,
            #         'amount': result,
            #     }))


            invoice_obj = self.env['account.move']
            vals = {
                'invoice_line_ids': line_vals,
                'rental_lines_id': rental_vals,
                'partner_id': selected_records[0].name.id,
                'branch_id': selected_records[0].branch_id.id,
                'invoice_date': datetime.today(),
                'state': 'draft',
                'journal_id': j.id,
                'fiscal_position_id': selected_records[0].branch_id.fiscal_position_id.id,
                'rental': selected_records.ids,
                'move_type': 'out_invoice',

            }
            ac = invoice_obj.create(vals)

    inv_counter = fields.Integer(compute='get_inv_counter')

    def get_inv_counter(self):
        for rec in self:
            count = self.env['account.move'].search_count([('rental', '=', self.ids)])
            rec.inv_counter = count

    def get_invoice_rental(self):
        return {
            'name': _('Invoice'),
            'domain': [('rental', '=', self.ids)],
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
