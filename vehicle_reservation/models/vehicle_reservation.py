from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class VehicleReservation(models.Model):
    _name = "vehicle.reservation"
    _description = "Vehicle Reservation"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'reservation_bf'

    reservation_bf = fields.Char(string='Reservation Number', copy=False, readonly=True, default='New')
    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True)
    # booking_id = fields.Many2one('booking.wizard', string="Booking", tracking=True)
    partner_id = fields.Many2one('res.partner', string="Customer", tracking=True,
                                 domain=[('partner_type', '=', 'is_customer')])
    rentee_type = fields.Selection([
        ('mr', 'MR.'),
        ('mrs', 'MRS.'),
        ('prof', 'Prof.'),
        ('dr', 'Dr.'),
    ], default='mr' ,string="Rentee Name")
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    booking = fields.Selection([
        ('chauffeur_driven', 'Chauffeur Driven'),
        ('self_drive', 'Self Drive'),
        ('driver', 'Driver')], default='chauffeur_driven', string="Booking")
    based_on = fields.Selection([
        ('time_and_mileage', 'Time And Mileage'),
        ('drop_off_duty', 'Drop Off Duty'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'), ('airport_duty', 'Airport Transfer') ,('out_station', 'Out Station')], default='time_and_mileage', string="Based On")
    payment_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit', 'Credit')], default='cash', string="Payment Type")
    vehicle_out = fields.Datetime('Vehicle Out')
    report_timing = fields.Datetime('Report Timing')
    model_id = fields.Many2one('fleet.vehicle.model', string="Model", tracking=True)
    brand_id = fields.Many2one('fleet.vehicle', string="Vehicle", tracking=True)
    brand_ids = fields.Many2many('fleet.vehicle' , compute = "_compute_brand_ids")
    # , compute = "_compute_brand_ids"
    booking_accept = fields.Selection([
        ('on_call', 'On Call'),
        ('by_email', 'By Email'), ('on_portal', 'On Portal'), ('on_mobile_app', 'On Mobile App'),
    ], default='on_call', string="Booking Received")
    source_name = fields.Char(string='Source Name')
    source_mobile_number = fields.Char(string='Source Mobile Number')
    rentee_mobile_number = fields.Char(string='Rentee Mobile Number')
    po_reference_req = fields.Boolean(string='Require PO Reference', compute="_compute_po_ref")
    po_reference = fields.Char(string='PO Reference')

    pickup = fields.Text(string='Pickup')
    program = fields.Text(string='Program')

    state = fields.Selection([('draft', 'In Progress'), ('confirm', 'confirmed'), ('cancel', 'Cancelled')], default='draft',
                             string="status", tracking=True)

    @api.onchange('partner_id')
    def _compute_po_ref(self):
        if self.partner_id:
            if self.partner_id.po_reference_req:
                self.po_reference_req = True
            else:
                self.po_reference_req = False
        else:
            self.po_reference_req = False

    # @api.model
    # def create(self, values):
    #     if 'branch_id' in values:
    #         seq = self.env['ir.sequence'].search(
    #             [('name', '=', 'Vehicle Reservation'), ('branch_id', '=', values['branch_id'])])
    #         self.env['ir.sequence'].next_by_code(seq.code)
    #         values['reservation_bf'] = seq.prefix + '-' + seq.branch_id.code + '-' + str(seq.number_next_actual) or _(
    #             'New')
    #     return super(VehicleReservation, self).create(values)

    def write(self, vals):
        if 'branch_id' in vals:
            seq = self.env['ir.sequence'].search(
                [('name', '=', 'Vehicle Reservation'), ('branch_id', '=', vals['branch_id'])])
            self.env['ir.sequence'].next_by_code(seq.code)
            vals['reservation_bf'] = seq.prefix + '-' + seq.branch_id.code + '-' + str(seq.number_next_actual) or _(
                'New')
        user = super(VehicleReservation, self).write(vals)
        return user


    def action_confirm(self):
        for rec in self:
            record = self.env['res.contract'].search(
                [('partner_id', '=', rec.partner_id.id)])
            print(record.contract_lines_id)
            # result = record.contract_lines_id.model_id.browse(rec.model_id)
            # print("lines",result)
            if record:
                bol = False
                for r in record.contract_lines_id:
                    print(r.model_id)
                    print(rec.model_id)
                    if r.model_id.name == rec.model_id.name and r.model_id.model_year == rec.model_id.model_year and r.model_id.power_cc == rec.model_id.power_cc:
                        print(r)
                        if record.state == 'confirm':
                            result = self.env['fleet.vehicle.state'].search([('sequence', '=', 1)])
                            rec.brand_id.state_id = result.id
                            rec.state = 'confirm'
                            vals = {
                                'name': rec.partner_id.id,
                                'rentee_type': rec.rentee_type,
                                'first_name': rec.first_name,
                                'last_name': rec.last_name,
                                'vehicle_no': rec.brand_id.id,
                                'mobile': rec.partner_id.mobile,
                                'time_out': rec.vehicle_out,
                                'branch_id': rec.branch_id.id,
                                'source': rec.id,
                                'based_on': rec.based_on,
                                'payment_type': rec.payment_type,
                                'pickup': rec.pickup,
                                'program': rec.program,
                                'reservation_id': rec.id,
                            }
                            self.env['rental.progress'].create(vals)
                            bol = True
                        else:
                            raise ValidationError(f'Please Confirm his "Contract" first')
                if not bol:
                    raise ValidationError(f'Please Define Model in Customer Contract')

            else:
                raise ValidationError(f'PLease Create Contract of Customer')
    # def action_confirm(self):
    #     for rec in self:
    #         record = self.env['res.contract'].search(
    #             [('partner_id', '=', rec.partner_id.id)])
    #         if record:
    #             for r in record:
    #                 if r.model_id.id == rec.brand_id.model_id.id:
    #                     if r.state == 'confirm':
    #                         if rec.based_on == 'daily':
    #                            print(record.per_day_rate)
    #                         elif rec.based_on == 'weekly':
    #                             print(record.per_week_rate)
    #                         elif rec.based_on == 'monthly':
    #                             print(record.per_month_rate)
    #                         result = self.env['fleet.vehicle.state'].search([('sequence', '=', 1)])
    #                         rec.brand_id.state_id = result.id
    #                         rec.state = 'confirm'
    #                         vals = {
    #                             'name': self.partner_id.id,
    #                             'vehicle_no': self.brand_id.id,
    #                             'mobile': self.partner_id.mobile,
    #                             'time_out': self.vehicle_out,
    #                             'branch_id': self.branch_id.id,
    #                             'source': self.reservation_bf,
    #                             'based_on': self.based_on,
    #                             'payment_type': self.payment_type,
    #                             'reservation_id': self.id,
    #                         }
    #                         self.env['rental.progress'].create(vals)
    #                     else:
    #                         raise ValidationError(f'Please Confirm his "Contract" first')
    #         else:
    #             raise ValidationError(f'Please Create Contract of Customer')

    def action_reset_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'

    @api.depends('model_id', 'brand_id')
    def _compute_brand_ids(self):
        for rec in self:
            records = self.env['fleet.vehicle'].search([('model_id.name', '=', rec.model_id.name),('model_id.model_year', '=', rec.model_id.model_year),('model_id.power_cc', '=', rec.model_id.power_cc)])
            vehicle_list = []
            if records:
                for re in records:
                    if re.state_id.sequence in [0, 1]:
                        vehicle_list.append(re.id)
                        rec.brand_ids = vehicle_list
                    else:
                        rec.brand_ids = []
            else:
                rec.brand_ids = []

    def rental_in_progress(self):
        return {
            'name': _('Rental In Progress'),
            'domain': [('reservation_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'rental.progress',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    rental_counter = fields.Integer(string='Invoice', compute='get_rental_counter')

    def get_rental_counter(self):
        for rec in self:
            count = self.env['rental.progress'].search_count([('reservation_id', '=', self.id)])
            rec.rental_counter = count

