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
        ('monthly', 'Monthly'), ('yearly', 'Yearly')], default='daily', string="Based On")
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit', 'Credit')], default='cash', string="Payment Type")
    mobile = fields.Char(string="Mobile", tracking=True, related='name.mobile')
    km_in = fields.Integer(string="Kms In", tracking=True)
    km_out = fields.Integer(string="Kms Out", tracking=True)
    driven = fields.Integer(string="Driven", tracking=True, compute="_compute_driven", readonly=True)
    toll = fields.Integer(string="Toll", tracking=True)
    allowa = fields.Integer(string="Allowa.", tracking=True)
    time_in = fields.Datetime('Time In')
    time_out = fields.Datetime('Time Out')
    days = fields.Integer(string='Days' ,readonly="1" , compute="_compute_calculate_date")
    note = fields.Text(string='Note')
    out_of_station = fields.Boolean(default=False)
    over_night = fields.Boolean(default=False)
    button_show = fields.Boolean(default=False)

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

    @api.depends('time_in', 'time_out')
    def _compute_calculate_date(self):
        if self.time_out and self.time_in:
             self.days = (self.time_in- self.time_out).days
        else:
            self.days = 0

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
        # for rec in self:
        #     if rec.km_out > 0:
        #         rec.state = 'chauffeur_out'
        #     else:
        #         raise ValidationError(f'Please enter some value of KM OUT')
        #     record = rec.env['fleet.vehicle.state'].search([('sequence', '=', 2)])
        #     for r in record:
        #         rec.vehicle_no.state_id = r.id

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
            'type': 'ir.actions.act_window',}


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
            record = self.env['res.contract'].search(
                [('partner_id', '=', rec.name.id),
                 ('state', '=', 'confirm')])
            i = 0
            print("helloo")
            for j in record.contract_lines_id:
                print("hy", j)
                if j.model_id.name == rec.vehicle_no.model_id.name:
                    print("Done")
                    if rec.based_on == 'daily':
                        i = j.per_day_rate
                    elif rec.based_on == 'weekly':
                        i = j.per_week_rate
                    elif rec.based_on == 'monthly':
                        i = j.per_month_rate
                    line_vals = []
                    line_vals.append((0, 0, {
                        'product_id': self.vehicle_no.product_id.id,
                        'analytic_account_id': self.vehicle_no.analytical_account_id.id,
                        'date_rental': self.time_out,
                        'rental_id': self.id,
                        'rentee_name': self.rentee_name,
                        'price_unit': self.days*i,
                    }))
                    invoice = {
                        'invoice_line_ids': line_vals,
                        'partner_id': self.name.id,
                        'invoice_date': date.today(),
                        'branch_id': self.branch_id.id,
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
            for r in selected_records:
                record = self.env['res.contract'].search(
                    [('partner_id', '=', r.name.id),
                     ('state', '=', 'confirm')])
                i = 0
                for j in record.contract_lines_id:
                    if j.model_id == r.vehicle_no.model_id.id:
                        if r.based_on == 'daily':
                            i = j.per_day_rate
                        elif r.based_on == 'weekly':
                            i = j.per_week_rate
                        elif r.based_on == 'monthly':
                            i = j.per_month_rate
                    line_vals.append(({
                        'product_id': r.vehicle_no.product_id.id,
                        'analytic_account_id': r.vehicle_no.analytical_account_id.id,
                        'date_rental': r.time_out,
                        'rental_id': r.id,
                        'rentee_name': r.rentee_name,
                        'price_unit': r.days * i,
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
