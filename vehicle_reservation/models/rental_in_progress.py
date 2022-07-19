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
    rentee_name = fields.Char(string='Rentee Name')
    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True, required=True)
    vehicle_no = fields.Many2one('fleet.vehicle', string="Vehicle", tracking=True)
    driver_id = fields.Many2one('res.partner', string="Driver", tracking=True,
                                domain=[('partner_type', '=', 'is_driver')])
    odometer = fields.Integer(compute='_get_odometer', string='Current Meter Reading',
                              help='Odometer measure of the vehicle at the moment of this log')
    source = fields.Char(string='Source')
    based_on = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'), ('airport', 'Airport')], default='daily', string="Based On")
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit', 'Credit')], default='cash', string="Payment Type")
    mobile = fields.Char(string="Mobile", tracking=True, related='name.mobile')
    km_in = fields.Integer(string="Kms In", tracking=True)
    km_out = fields.Integer(string="Kms Out", tracking=True)
    toll = fields.Integer(string="Toll", tracking=True)
    allowa = fields.Integer(string="Allowa.", tracking=True)
    time_in = fields.Datetime('Time In')
    time_out = fields.Datetime('Time Out')
    note = fields.Text(string='Note')
    out_of_station = fields.Boolean(default=False)
    over_night = fields.Boolean(default=False)
    button_show = fields.Boolean(default=False)

    hours = fields.Integer(string='Hours')
    per_hour_rate = fields.Integer(string='Hour Rate')
    days = fields.Integer(string='Days')
    day_rate = fields.Integer(string='Day Rate')
    weeks = fields.Integer(string='Weeks')
    week_rate = fields.Integer(string='Week Rate')
    months = fields.Integer(string='Months')
    month_rate = fields.Integer(string='Month Rate')
    airport_rate = fields.Integer(string='Airport Rate')
    extra_airport_km = fields.Integer(string='Extra KMs(Airport)')
    extra_airport_hour = fields.Integer(string='Extra Hours(Airport)')
    total_rate = fields.Integer(string='Total Rate')
    driven = fields.Integer(string="Driven", tracking=True, compute="_compute_driven")
    apply_out_station = fields.Integer(string='Apply Out Station After')
    out_station_rate = fields.Integer(string='Out Station Rate')
    net_amount = fields.Integer(string='Net Amount')

    state = fields.Selection(
        [('ready_for_departure', 'Ready For Departure'), ('chauffeur_out', 'Chauffeur Out'),
         ('chauffeur_in', 'Chauffeur In'),
         ('rental_close', 'Rental Closed')],
        default='ready_for_departure',
        string="Status", tracking=True)
    reservation_id = fields.Many2one('vehicle.reservation')
    stage_id = fields.Selection([
        ('billed', 'BILLED'),
        ('not_billed', 'NOT BILLED')], default='not_billed', string="Stage ID")

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
            for j in record.contract_lines_id:
                if j.model_id.name == self.vehicle_no.model_id.name and j.model_id.model_year == self.vehicle_no.model_id.model_year and j.model_id.power_cc == self.vehicle_no.model_id.power_cc:
                    if self.apply_out_station <= self.driven:
                        self.out_station_rate = j.out_station
                        self.net_amount = self.total_rate + self.out_station_rate
                    else:
                        pass
        else:
            self.net_amount = self.net_amount - self.out_station_rate

    @api.onchange('time_in', 'time_out')
    def _onchange_calculate_dwm(self):
        if self.time_out and self.time_in:
            # total_days = (self.time_in - self.time_out).days
            total_days = (self.time_in - self.time_out)
            if total_days:
                # year = int(total_days / 365)
                # month = int((total_days - (year * 365)) / 30)
                # week = int((total_days - (year * 365)) - month * 30) // 7
                # day = int((total_days - (year * 365)) - month * 30 - week * 7)
                record = self.env['res.contract'].search(
                    [('partner_id', '=', self.name.id),
                     ('state', '=', 'confirm')])
                i = 0
                td = str(total_days).split(',')
                td = td[-1].replace(' ', '')
                hours = datetime.strptime(str(td), "%H:%M:%S").hour
                minutes = datetime.strptime(str(td), "%H:%M:%S").minute
                extra_km_rate = 0
                for j in record.contract_lines_id:
                    if j.model_id.name == self.vehicle_no.model_id.name and j.model_id.model_year == self.vehicle_no.model_id.model_year and j.model_id.power_cc == self.vehicle_no.model_id.power_cc:
                        self.per_hour_rate = j.per_hour_rate
                        if self.based_on == 'daily':
                            if minutes > 0:
                                self.hours = hours + 1
                                self.per_hour_rate = j.per_hour_rate
                            else:
                                self.hours = hours
                                self.per_hour_rate = j.per_hour_rate
                            self.days = total_days.days
                            self.day_rate = j.per_day_rate
                            self.total_rate = (self.days * self.day_rate) + (self.hours * self.per_hour_rate)
                            if self.apply_out_station <= self.driven:
                                self.out_of_station = True
                                self.apply_out_station = record.apply_out_station
                                self.out_station_rate = j.out_station
                                self.net_amount = self.total_rate + self.out_station_rate
                            else:
                                self.net_amount = self.total_rate
                                self.out_station_rate = 0
                        elif self.based_on == 'weekly':
                            week = int(total_days.days // 7)
                            day = int(total_days.days - week * 7)
                            # hours = datetime.strptime(str(total_days).replace(' days', ''), "%d, %H:%M:%S").hour
                            # minutes = datetime.strptime(str(total_days).replace(' days', ''), "%d, %H:%M:%S").minute
                            if minutes > 0:
                                self.hours = hours + 1
                                self.per_hour_rate = j.per_hour_rate
                            else:
                                self.hours = hours
                                self.per_hour_rate = j.per_hour_rate
                            print("Weekly")
                            print(week)
                            print(day)
                            self.days = day
                            self.weeks = week
                            self.day_rate = j.per_day_rate
                            self.week_rate = j.per_week_rate
                            self.total_rate = ((self.days * self.day_rate) + (
                                    self.weeks * self.week_rate) + (self.hours * self.per_hour_rate))
                            if self.apply_out_station <= self.driven:
                                print("Out Station")
                                self.out_of_station = True
                                self.apply_out_station = record.apply_out_station
                                self.out_station_rate = j.out_station
                                self.net_amount = self.total_rate + self.out_station_rate
                            else:
                                self.net_amount = self.total_rate
                                self.out_station_rate = 0
                        elif self.based_on == 'monthly':
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
                                self.hours = hours + 1
                                self.per_hour_rate = j.per_hour_rate
                            else:
                                self.hours = hours
                                self.per_hour_rate = j.per_hour_rate
                            print("monthly")
                            self.days = day
                            self.weeks = week
                            self.months = month
                            self.day_rate = j.per_day_rate
                            self.week_rate = j.per_week_rate
                            self.month_rate = j.per_month_rate
                            print("Total month", self.months)
                            print("Total week", self.weeks)
                            print("Total day", self.days)
                            print("Rate month", self.month_rate)
                            print("Rate week", self.week_rate)
                            print("Rate day", self.day_rate)
                            print("Driven", self.driven)
                            self.total_rate = ((self.days * self.day_rate) + (self.weeks * self.week_rate) + (
                                    self.months * self.month_rate) + (self.hours * self.per_hour_rate) + j.mobil_oil_rate + j.oil_filter_rate + j.air_filter_rate)
                            if self.apply_out_station <= self.driven:
                                print("Out Station")
                                self.out_of_station = True
                                self.apply_out_station = record.apply_out_station
                                self.out_station_rate = j.out_station
                                self.net_amount = self.total_rate + self.out_station_rate
                            else:
                                self.net_amount = self.total_rate
                                self.out_station_rate = 0
                        elif self.based_on == 'airport':
                            print("hours", hours)
                            print("minute", minutes)
                            self.airport_rate = j.airport_rate
                            extra_km = self.driven - record.km_limit
                            print("Extra kmmm", extra_km)
                            extra_hour = hours - record.hourly_limit
                            print("Extra ho", extra_hour)
                            if extra_km > 0:
                                print("Extra KM" , extra_km)
                                self.extra_airport_km = extra_km
                                extra_km_rate = extra_km * record.addit_km_rate
                                # self.total_rate = ((self.days * self.day_rate) + (self.weeks * self.week_rate) + (
                                #         self.months * self.month_rate) + self.airport_rate + extra_km_rate)
                            if extra_hour > 0:
                                print("Extra Hour" , extra_hour)
                                if minutes > 0:
                                    print("minut")
                                    self.hours = hours + 1
                                    print("Hours After Minute" , self.hours)
                                    self.per_hour_rate = record.addit_hour_rate
                                    self.extra_airport_hour = extra_hour + 1
                                else:
                                    self.hours = hours
                                    self.per_hour_rate = record.addit_hour_rate
                                    self.extra_airport_hour = extra_hour
                                print("True")
                            self.total_rate = ((self.days * self.day_rate) + (self.weeks * self.week_rate) + (
                                    self.months * self.month_rate) + (self.extra_airport_hour * self.per_hour_rate) + self.airport_rate  + extra_km_rate)
                            self.net_amount = self.total_rate
                            # else:
                            #     self.hours = hours
                            #     self.week_rate = record.addit_hour_rate
                            #     self.total_rate = ((self.days * self.day_rate) + (self.weeks * self.week_rate) + (
                            #             self.months * self.month_rate) + (self.hours * self.per_hour_rate) + extra_rate)
                            #     self.net_amount = self.total_rate

                            # else:
                            #     self.total_rate = ((self.days * self.day_rate) + (self.weeks * self.week_rate) + (
                            #             self.months * self.month_rate) + (self.hours * self.per_hour_rate) + (self.airport_rate))
                            #     self.net_amount = self.total_rate

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
                self.airport_rate = 0
        else:
            self.days = 0
            self.weeks = 0
            self.months = 0
            self.day_rate = 0
            self.week_rate = 0
            self.month_rate = 0
            self.airport_rate = 0

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

    # def action_chauffeur_in(self):
    #     for rec in self:
    #         if rec.km_in > rec.km_out:
    #             rec.state = 'chauffeur_in'
    #         elif rec.km_in < rec.km_out:
    #             raise ValidationError(f'Please enter value greater than KM Out')
    #         record = self.env['res.contract'].search(
    #             [('partner_id', '=', rec.name.id), ('model_id', '=', rec.vehicle_no.model_id.id),
    #              ('state', '=', 'confirm')])
    #         for r in record:
    #             year = int(rec.days / 365)
    #             month = int((rec.days - (year * 365)) / 30)
    #             week = int((rec.days - (year * 365)) - month * 30) // 7
    #             day = int((rec.days - (year * 365)) - month * 30 - week * 7)
    #             print("year" , year)
    #             print("month", month)
    #             print("week" , week)
    #             print("days" , day)
    #             # print("time" , self.time_in - timedelta(days=day))
    #             # a = timedelta(days=0)
    #             if year > 0:
    #                 # a = self.time_out + timedelta(days=365)
    #                 print(r.per_year_rate)
    #                 vals = {
    #                     'partner_id': self.name.id,
    #                     'vehicle_id': self.vehicle_no.id,
    #                     'start_date': self.time_out,
    #                     # 'expiration_date': self.time_in,
    #                     'expiration_date': self.time_out + timedelta(days=(365*year)),
    #                     'cost_frequency': 'yearly',
    #                     'cost_generated': r.per_year_rate,
    #                     # 'reservation_id': self.id,
    #                 }
    #                 self.env['fleet.vehicle.log.contract'].create(vals)
    #             if month > 0:
    #                 print(r.per_month_rate)
    #                 vals = {
    #                     'partner_id': self.name.id,
    #                     'vehicle_id': self.vehicle_no.id,
    #                     'start_date': self.time_out,
    #                     'expiration_date': self.time_out + timedelta(days=(30*month)),
    #                     # 'expiration_date': self.time_in,
    #                     'cost_frequency': 'monthly',
    #                     'cost_generated': r.per_month_rate,
    #                     # 'reservation_id': self.id,
    #                 }
    #                 self.env['fleet.vehicle.log.contract'].create(vals)
    #             if week > 0:
    #                 print(r.per_week_rate)
    #                 vals = {
    #                     'partner_id': self.name.id,
    #                     'vehicle_id': self.vehicle_no.id,
    #                     'start_date': self.time_out,
    #                     'expiration_date': self.time_out + timedelta(days=(7*week)),
    #                     # 'expiration_date': self.time_in,
    #                     'cost_frequency': 'weekly',
    #                     'cost_generated': r.per_week_rate,
    #                     # 'reservation_id': self.id,
    #                 }
    #                 self.env['fleet.vehicle.log.contract'].create(vals)
    #             if day > 0:
    #                 print(r.per_day_rate)
    #
    #                 vals = {
    #                     'partner_id': self.name.id,
    #                     'vehicle_id': self.vehicle_no.id,
    #                     'start_date': self.time_out,
    #                     'expiration_date': self.time_out + timedelta(days=(day)),
    #                     # 'expiration_date': self.time_in,
    #                     'cost_frequency': 'daily',
    #                     'cost_generated': r.per_day_rate,
    #                     # 'reservation_id': self.id,
    #                 }
    #                 self.env['fleet.vehicle.log.contract'].create(vals)

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

    def _compute_driven(self):
        for rec in self:
            rec.driven = rec.km_in - rec.km_out

    def action_create_invoice(self):
        for rec in self:
            # record = self.env['res.contract'].search(
            #     [('partner_id', '=', rec.name.id),
            #      ('state', '=', 'confirm')])
            # i = 0
            # print("helloo")
            # for j in record.contract_lines_id:
            #     print("hy", j)
            #     if j.model_id.name == rec.vehicle_no.model_id.name:
            #         print("Done")
            #         if rec.based_on == 'daily':
            #             i = j.per_day_rate
            #         elif rec.based_on == 'weekly':
            #             i = j.per_week_rate
            #         elif rec.based_on == 'monthly':
            #             i = j.per_month_rate
            line_vals = []
            line_vals.append((0, 0, {
                'product_id': self.vehicle_no.product_id.id,
                'analytic_account_id': self.vehicle_no.analytical_account_id.id,
                'date_rental': self.time_out,
                'rental_id': self.id,
                'rentee_name': self.rentee_name,
                'price_unit': self.net_amount,
            }))
            r = self.env['account.journal'].search([('branch_id', '=', self.branch_id.id), ('type', '=', 'sale')])
            print(r)
            invoice = {
                'invoice_line_ids': line_vals,
                'partner_id': self.name.id,
                'invoice_date': date.today(),
                'branch_id': self.branch_id.id,
                'journal_id': r.id,
                'fiscal_position_id': self.branch_id.fiscal_position_id.id,
                'rental': self.ids,
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
            j = self.env['account.journal'].search([('branch_id', '=', self.branch_id.id), ('type', '=', 'sale')])
            for r in selected_records:
                # record = self.env['res.contract'].search(
                #     [('partner_id', '=', r.name.id),
                #      ('state', '=', 'confirm')])
                # i = 0
                # for j in record.contract_lines_id:
                #     if j.model_id == r.vehicle_no.model_id.id:
                #         if r.based_on == 'daily':
                #             i = j.per_day_rate
                #         elif r.based_on == 'weekly':
                #             i = j.per_week_rate
                #         elif r.based_on == 'monthly':
                #             i = j.per_month_rate
                line_vals.append(({
                    'product_id': r.vehicle_no.product_id.id,
                    'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                    'date_rental': r.time_out,
                    'rental_id': r.id,
                    'rentee_name': r.rentee_name,
                    'price_unit': r.net_amount,
                }))
                r.stage_id = 'billed'
                r.button_show = True
            print(line_vals)
            invoice_obj = self.env['account.move']
            vals = {
                'invoice_line_ids': line_vals,
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
