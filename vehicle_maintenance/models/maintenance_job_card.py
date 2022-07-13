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
    location_id = fields.Many2one('stock.warehouse', string="Location", tracking=True)

    inspection_from = fields.Char(string='Inspection From')
    vehicle_in = fields.Datetime('Vehicle In', default=datetime.today())
    vehicle_out = fields.Datetime('Vehicle Out')
    registration_no = fields.Char(string='Registration No')
    model_id = fields.Many2one('fleet.vehicle.model', string="Model", tracking=True)
    chassis_no = fields.Char(string='Chassis No')
    next_oil_change = fields.Integer(string='Next Oil Change')
    current_km = fields.Integer(string='Current KM')
    work_done = fields.Text(string='Work Done')

    state = fields.Selection(
        [('waiting_for_inspection', 'Waiting For Inspection'), ('under_maintenance', 'Under Maintenance'),
         ('completed', 'Maintenance Completed'),
         ('vehicle_out', 'Vehicle Out')], default='waiting_for_inspection',
        string="Stage", tracking=True)

    @api.model
    def create(self, values):
        if 'branch_id' in values:
            seq = self.env['ir.sequence'].search(
                [('name', '=', 'Vehicle Maintenance'), ('branch_id', '=', values['branch_id'])])
            self.env['ir.sequence'].next_by_code(seq.code)
            values['maintenance_bf'] = seq.prefix + '/' + seq.branch_id.code + '/' + str(
                datetime.now().year) + '/' + str(datetime.now().month) + '/' + str(seq.number_next_actual) or _('New')
        return super(VehicleMaintenance, self).create(values)

    def action_under_maintenance(self):
        self.state = 'under_maintenance'

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
