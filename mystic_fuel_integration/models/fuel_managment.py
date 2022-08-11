from odoo import api, fields, models, _


class FuelManagement(models.Model):
    _name = "fuel.management"
    _description = "Fuel Management"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Fuel Number', copy=False, readonly=True, default='New')
    brand_id = fields.Many2one('fleet.vehicle', string="Vehicle", tracking=True)
    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True)
    fuel_type = fields.Selection([
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('lpg', 'LPG'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
    ], 'Fuel Type', help='Fuel Used by the vehicle', related='brand_id.fuel_type')
    # odometer = fields.Integer(compute='_get_odometer', string='Current Meter Reading',
    #                           help='Odometer measure of the vehicle at the moment of this log')
    driver_id = fields.Many2one('hr.employee', string="Driver", tracking=True,
                                domain=[('is_driver', '=', True)])
    journal_id = fields.Many2one('account.journal', string="Journal")

    fuel_lines_id = fields.One2many('fuel.lines', 'fuel_id', string='Fuel Lines')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'confirmed'), ('cancel', 'Cancelled')],
                             default='draft',
                             string="status", tracking=True)

    # @api.depends('branch_id')
    # def _get_odometer(self):
    #     FleetVehicalOdometer = self.env['fleet.vehicle.odometer']
    #     for record in self:
    #         vehicle_odometer = FleetVehicalOdometer.search([('vehicle_id', '=', record.brand_id.id)], limit=1,
    #                                                        order='value desc')
    #         if vehicle_odometer:
    #             record.odometer = vehicle_odometer.value
    #         else:
    #             record.odometer = 0

    def action_confirm(self):
        active_model = self.env['fuel.management'].search([('id', '=', self.id)])
        print("active", active_model)
        bill = self.env['ir.config_parameter'].get_param('mystic_fuel_integration.product_refuel_id')
        expense = self.env['ir.config_parameter'].get_param('mystic_fuel_integration.product_expense_id')
        print(bill)
        print(type(bill))
        print(expense)
        product = self.env['product.product'].search([('id', '=', int(bill))])
        print(product)
        for lines in active_model.fuel_lines_id:
            print(lines)
            line_vals = []
            if lines.entry_type == 'card':
                print("card")
                line_vals.append((0, 0, {
                    'product_id': int(bill),
                    'branch_id': active_model.branch_id.id,
                    # 'account_id': product.property_account_expense_id.id,
                    'analytic_account_id': active_model.brand_id.analytical_account_id.id,
                    'analytic_tag_ids': active_model.branch_id.analytical_account_tag_id.id,
                    'quantity': lines.qty,
                    'price_unit': lines.rate,
                }))
                self.env['account.move'].create({
                    'invoice_line_ids': line_vals,
                    'partner_id': lines.vendor_id.id,
                    'branch_id': active_model.branch_id.id,
                    'state': 'draft',
                    'journal_id': active_model.journal_id.id,
                    # 'fiscal_position_id':.id,
                    # 'rental': selected_records.ids,
                    'move_type': 'in_invoice',
            })
            elif lines.entry_type == 'slip':
                print("slip")
                self.env['hr.expense'].create({
                    'name': lines.description,
                    'product_id': int(expense),
                    'unit_amount': lines.rate,
                    'quantity': lines.qty,
                    'payment_mode': lines.payment_mode,
                    'employee_id': active_model.driver_id.id,
                    'analytic_account_id': active_model.brand_id.analytical_account_id.id,
                    'analytic_tag_ids': active_model.branch_id.analytical_account_tag_id.id,
                })
        self.state = 'confirm'

    def action_reset_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'

    @api.onchange('brand_id', 'branch_id')
    def _onchange_model(self):
        if self.brand_id:
            self.branch_id = self.brand_id.branch_id.id

    @api.model
    def create(self, values):
        if 'branch_id' in values:
            seq = self.env['ir.sequence'].search(
                [('name', '=', 'Fuel Management'), ('branch_id', '=', values['branch_id'])])
            self.env['ir.sequence'].next_by_code(seq.code)
            values['name'] = seq.prefix + '-' + seq.branch_id.code + '-' + str(seq.number_next_actual) or _(
                'New')
        return super(FuelManagement, self).create(values)

    def action_add_fuel(self):
        # result = self.env['fuel.management'].browse(self.env.context.get('active_ids'))
        print(self.id)
        active_model = self.env['fuel.management'].search([('id' , '=' , self.id)])
        print("active",active_model)
        lines = active_model.fuel_lines_id
        print(lines)
        value = 0
        if lines:
            value = lines[-1].km_in
        else:
            value= 0
        return {
            'name': _('Add Fuel'),
            'res_model': 'addfuel.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'fuel.management',
                'default_km_out': value ,
            },
            'target': 'new',
            'type': 'ir.actions.act_window', }


class FuelManagementLines(models.Model):
    _name = "fuel.lines"
    _description = "Fuel Management Lines"

    date = fields.Date(string="Date", tracking=True)
    entry_type = fields.Selection([
        ('card', 'Card'),
        ('slip', 'Slip'),
    ], 'Entry Type')
    description = fields.Char(string='Description')
    ref_no = fields.Char(string='Ref#')
    km_in = fields.Integer(string='Km In')
    km_out = fields.Integer(string='Km Out')
    diff = fields.Integer(string='Diff')
    qty = fields.Float(string='Qty')
    mpg = fields.Float(string='MPG')
    rate = fields.Float(string='Rate')
    amount = fields.Float(string='Amount')
    rs_per_km = fields.Float(string='Rs./km')
    vendor_id = fields.Many2one('res.partner', string="Vendor", tracking=True,
                                domain=[('partner_type', '=', 'is_pump')])
    payment_mode = fields.Selection([
        ("own_account", "Employee (to reimburse)"),
        ("company_account", "Company")
    ], tracking=True, string="Paid By")

    fuel_id = fields.Many2one('fuel.management')


class AccountSettingCategory(models.TransientModel):
    _inherit = 'res.config.settings'

    product_refuel_id = fields.Many2one('product.product', string='Product',
                                        config_parameter='mystic_fuel_integration.product_refuel_id')
    product_expense_id = fields.Many2one('product.product', string='Product',
                                         config_parameter='mystic_fuel_integration.product_expense_id')
