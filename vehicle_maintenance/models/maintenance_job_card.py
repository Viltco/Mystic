from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime


class VehicleMaintenance(models.Model):
    _name = "vehicle.maintenance"
    _description = "Vehicle Maintenance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'maintenance_bf'

    maintenance_bf = fields.Char(string='Maintenance Number', copy=False, default='New')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", tracking=True)
    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True)
    driver_id = fields.Many2one('res.partner', string="Driver", tracking=True,
                                domain=[('partner_type', '=', 'is_driver')])
    opertion_type_id = fields.Many2one('stock.picking.type', string="Operation Type", tracking=True)
    location_id = fields.Many2one('stock.location', string="Location", tracking=True,
                                  related='opertion_type_id.default_location_src_id')

    inspection_from = fields.Char(string='Inspection From')
    vehicle_in = fields.Datetime('Vehicle In', default=datetime.today())
    vehicle_out = fields.Datetime('Vehicle Out')
    registration_no = fields.Char(string='Registration No')
    model_id = fields.Many2one('fleet.vehicle.model', string="Model", tracking=True)
    chassis_no = fields.Char(string='Chassis No')
    next_oil_change = fields.Integer(string='Next Oil Change')
    current_km = fields.Integer(string='Current KM')
    work_done = fields.Text(string='Work Done')
    fuel_type = fields.Selection([
        ('gasoline', 'Gasoline'),
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('cng', 'CNG')], string="Fuel Type")

    state = fields.Selection(
        [('waiting_for_inspection', 'Waiting For Inspection'), ('under_maintenance', 'Under Maintenance'),
         ('completed', 'Maintenance Completed'),
         ('vehicle_out', 'Vehicle Out')], default='waiting_for_inspection',
        string="Stage", tracking=True)
    total = fields.Float(string='Total', store=True, compute="_compute_total")
    labour_total = fields.Float(string='Labour', store=True, compute="_compute_labour_total")
    tax = fields.Float(string='Tax', store=True)
    grand_total = fields.Float(string='Grand Total', store=True, compute="_compute_grand_total")

    maintenance_lines_id = fields.One2many('vehicle.maintenance.lines', 'maintenance_job_id',
                                           string="Maintenance Lines")

    @api.depends('maintenance_lines_id.total')
    def _compute_total(self):
        total = 0
        for rec in self:
            for line in rec.maintenance_lines_id:
                total += line.total
            rec.total = total

    @api.depends('maintenance_lines_id.labour')
    def _compute_labour_total(self):
        labour = 0
        for rec in self:
            for line in rec.maintenance_lines_id:
                labour += line.labour
            rec.labour_total = labour

    @api.depends('total', 'labour_total')
    def _compute_grand_total(self):
        for rec in self:
            rec.grand_total = rec.total + rec.labour_total + rec.tax

    @api.model
    def create(self, values):
        line_vals = []
        if 'branch_id' in values:
            seq = self.env['ir.sequence'].search(
                [('name', '=', 'Vehicle Maintenance'), ('branch_id', '=', values['branch_id'])])
            self.env['ir.sequence'].next_by_code(seq.code)
            values['maintenance_bf'] = seq.prefix + '/' + seq.branch_id.code + '/' + str(
                datetime.now().year) + '/' + str(datetime.now().month) + '/' + str(seq.number_next_actual) or _('New')
        # operation_type = self.env['stock.picking.type'].search(
        #     [('branch_id', '=', self.number), ('vehicle_id.license_plate', '=', False)])

        # line_vals.append((0, 0, {
        #     'product_id': self.non_pool_other_id.id,
        #     'analytic_account_id': r.vehicle_no.analytical_account_id.id,
        #     'date_rental': r.time_out,
        #     'rental_id': r.id,
        #     'rentee_name': r.first_name + '' + r.last_name,
        #     'price_unit': r.damage_charges,
        # }))
        # operation = str(values['opertion_type_id'])
        # print(operation)
        # res = self.env['stock.picking'].create(
        #     {
        #      'picking_type_id':  self.opertion_type_id,
        #      'location_id': [],
        #      'location_dest_id': [],
        #      # 'vehicle_id': rest.id,
        #      })
        return super(VehicleMaintenance, self).create(values)

    def action_under_maintenance(self):
        # res = self.env['stock.picking'].create(
        #     {
        #      'picking_type_id':  self.opertion_type_id.id,
        #      'location_id': self.opertion_type_id.default_location_src_id.id,
        #      'location_dest_id': self.opertion_type_id.default_location_dest_id.id,
        #      # 'move_ids_without_package': line_vals,
        #      # 'vehicle_id': rest.id,
        #      })
        # for line in self.maintenance_lines_id:
        #     lines = {
        #         # 'picking_id': picking.id,
        #         'product_id': line.product_id.id,
        #         'name': 'Transfer Out',
        #         # 'product_uom': line.product_id.uom_id.id,
        #         'location_id': self.opertion_type_id.default_location_src_id.id,
        #         'location_dest_id': self.opertion_type_id.default_location_dest_id.id,
        #         'product_uom_qty': line.quantity,
        #     }
        #     stock_move = self.env['stock.move'].create(lines)
        picking_delivery = self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1)
        vals = {
            'picking_type_id': self.opertion_type_id.id,
            'location_id': self.opertion_type_id.default_location_src_id.id,
            'location_dest_id': self.opertion_type_id.default_location_dest_id.id,
            # 'partner_id': self.workcenter_id.partner_id.id,
            # 'product_sub_id': self.product_subcontract_id.id,
            # 'picking_type_id': picking_delivery.id,
            'origin': self.maintenance_bf,
        }
        picking = self.env['stock.picking'].create(vals)
        for line in self.maintenance_lines_id:
            lines = {
                'picking_id': picking.id,
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_uom': line.product_id.uom_id.id,
                'location_id': self.opertion_type_id.default_location_src_id.id,
                'location_dest_id': self.opertion_type_id.default_location_dest_id.id,
                'product_uom_qty': line.quantity,
                # 'reserved_availability': qty * line.product_qty,
                # 'quantity_done': qty * line.product_qty,
            }
            stock_move = self.env['stock.move'].create(lines)
        self.state = 'under_maintenance'

    int_counter = fields.Integer(compute='get_int_counter')

    def get_int_counter(self):
        for rec in self:
            count = self.env['stock.picking'].search_count([('origin', '=', self.maintenance_bf)])
            rec.int_counter = count

    def get_internal_transfer(self):
        return {
            'name': _('Transfers'),
            'domain': [('origin', '=', self.maintenance_bf)],
            'view_type': 'form',
            'res_model': 'stock.picking',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def action_maintenance_completed(self):
        self.state = 'completed'

    def action_vehicle_out(self):
        self.state = 'vehicle_out'
        self.vehicle_out = datetime.today()

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.registration_no = self.vehicle_id.license_plate
            self.model_id = self.vehicle_id.model_id.id


class VehicleMaintenanceLines(models.Model):
    _name = "vehicle.maintenance.lines"

    product_id = fields.Many2one('product.product', string="Product", tracking=True)
    available_quantity = fields.Float(string='Available Quantity', store=True, compute="_compute_available_quantity")
    quantity = fields.Float(string='Quantity', store=True)
    unit_price = fields.Float(string='Unit Price', store=True, related='product_id.standard_price')
    total = fields.Float(string='Total', store=True, compute="_compute_total")
    labour = fields.Float(string='Labour', store=True)

    maintenance_job_id = fields.Many2one('vehicle.maintenance')

    @api.depends('quantity', 'unit_price')
    def _compute_total(self):
        for rec in self:
            if rec.quantity > rec.available_quantity:
                raise ValidationError(f'Please Enter quantity less than available quantity')
            else:
                rec.total = rec.quantity * rec.unit_price

    @api.depends('product_id', 'maintenance_job_id.opertion_type_id', 'maintenance_job_id.location_id')
    def _compute_available_quantity(self):
        for rec in self:
            total = 0
            quants = self.get_quant_lines()
            # print("quants",quants)
            quants = self.env['stock.quant'].browse(quants)
            for q_line in quants:
                # print(q_line.product_tmpl_id)
                print("locations", q_line.location_id)
                # print(rec.product_id)
                if q_line.product_tmpl_id.name == rec.product_id.name and q_line.location_id.id == rec.maintenance_job_id.location_id.id:
                    # if q_line.location_id.name == rec.maintenance_job_id.location_id.name:
                    print("after", q_line)
                    total = total + q_line.available_quantity
                    print(total)
            rec.available_quantity = total

    def get_quant_lines(self):
        domain_loc = self.env['product.product']._get_domain_locations()[0]
        quant_ids = [l['id'] for l in self.env['stock.quant'].search_read(domain_loc, ['id'])]
        return quant_ids
