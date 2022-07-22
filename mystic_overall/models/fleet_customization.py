from odoo import api, models, fields, _
from datetime import datetime
from datetime import date


class FleetState(models.Model):
    _inherit = "fleet.vehicle.state"

    color = fields.Char()


class FleetManageField(models.Model):
    _inherit = "fleet.vehicle"

    color = fields.Char(related='state_id.color')
    button_show = fields.Boolean(default=False)
    booleans = fields.Selection([
        ('pool_id', 'Pool'),
        ('non_pool', 'Non Pool'),
        ('non_pool_other', 'Non Pool Other')], default='pool_id', string="Fleet Type")

    analytical_account_id = fields.Many2one('account.analytic.account', string="Analytical Account")
    product_id = fields.Many2one('product.product', string="Product")
    branch_id = fields.Many2one('res.branch', string="Branch", tracking=True,
                                default=lambda self: self.env.user.branch_id)
    odometer = fields.Integer(compute='_get_odometer', inverse='_set_odometer', string='Current Meter Reading',
                              help='Odometer measure of the vehicle at the moment of this log')
    time_in = fields.Datetime('Time In', compute="_get_earliest_date")
    fleet_age = fields.Char('Fleet Age', compute="_compute_fleet_age")
    counter = fields.Char(string='Car Counter')
    model_year = fields.Char('Model Year', help='Year of the model', compute="_compute_model_year")

    account_asset_id = fields.Many2one('account.asset', string="Fixed Assets", domain="[('asset_show', '=', False)]")

    def _compute_model_year(self):
        self.model_year = self.model_id.model_year

    def name_get(self):
        print('gggg')
        res = []
        for rec in self:
            print((rec.id, '%s/%s/%s/%s' % (
            rec.model_id.brand_id.name, rec.model_id.name, rec.model_id.model_year, rec.model_id.power_cc)))
            if rec.license_plate:
                res.append((rec.id, '%s/%s/%s/%s/%s' % (
                rec.model_id.brand_id.name, rec.model_id.name, rec.model_id.model_year, rec.model_id.power_cc,
                rec.license_plate)))
            else:
                res.append((rec.id, '%s/%s/%s/%s/%s' % (
                rec.model_id.brand_id.name, rec.model_id.name, rec.model_id.model_year, rec.model_id.power_cc,
                rec.counter)))

        return res

    def write(self, values):
        print(self.account_asset_id)
        self.account_asset_id.vehicle_id = False
        self.account_asset_id.asset_show = False
        res = super(FleetManageField, self).write(values)
        self.account_asset_id.vehicle_id = self.id
        self.account_asset_id.asset_show = True
        return res

    @api.depends('account_asset_id')
    def _compute_fleet_age(self):
        if self.account_asset_id:
            dayss = (self.account_asset_id.acquisition_date - date.today()).days
            print(dayss)
            if dayss > 0:
                year = int(dayss / 365)
                month = int((dayss - (year * 365)) / 30)
                # week = int((dayss - (year * 365)) - month * 30) // 7
                day = int((dayss - (year * 365)) - month * 30)
                print("year", year)
                print("month", month)
                # print("week" , week)
                print("days", day)
                self.fleet_age = str(year) + "-year" + '/' + str(month) + '-Month' + '/' + str(day) + '-Day'
            else:
                self.fleet_age = 0
        else:
            self.fleet_age = 0

    @api.onchange('model_id', 'model_year')
    def _onchange_model(self):
        if self.model_id:
            self.model_year = self.model_id.model_year

    def _get_earliest_date(self):
        # dates = []
        # for rec in self:
        #     record = self.env['rental.progress'].search([('vehicle_no', '=', rec.id)])
        #     print(record)
        #     for r in record:
        #         if r:
        #             dates.append(r.time_in)
        #             print(dates)
        # print(dates)
        # l = dates.sort()
        # # print(l)
        self.time_in = datetime.today()

    # @api.model
    # def create(self, vals):
    #     res = super(FleetManageField, self).create(vals)
    #     # print(res)
    #     v = self.env['fleet.vehicle.model'].browse([vals['model_id']])
    #     result = self.env['account.analytic.account'].create(
    #         {'name': str(v.name) + '/' + str(v.brand_id.name) + '/' + str(v.model_year) + '/' + str(
    #             v.power_cc) + '/' + res['license_plate'],
    #          'fleet_vehicle_id': res.id,
    #          })
    #     res.analytical_account_id = result.id
    #     # result = self.env['product.product'].create(
    #     #     {'name': res['license_plate'],
    #     #      'fleet_vehicle_id': res.id,
    #     #      'branch_ids': res['branch_id'],
    #     #      'type': 'service',
    #     #      'invoice_policy': 'order',
    #     #      'purchase_method': 'purchase',
    #     #      })
    #     # res.product_id = result.id
    #     # result.product_tmpl_id.write({'fleet_vehicle_id': res.id})
    #     return res

    def _get_odometer(self):
        FleetVehicalOdometer = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = FleetVehicalOdometer.search([('vehicle_id', '=', record.id)], limit=1,
                                                           order='value desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    def _set_odometer(self):
        for record in self:
            if record.odometer:
                date = fields.Date.context_today(record)
                data = {'value': record.odometer, 'date': date, 'vehicle_id': record.id}
                self.env['fleet.vehicle.odometer'].create(data)

    po_counter = fields.Integer(string='PO', compute='get_po_counter')

    def get_po_counter(self):
        for rec in self:
            count = self.env['purchase.order'].search_count([('fleet_vehicle_id', '=', rec.id)])
            rec.po_counter = count

    #
    # def action_create_po(self):
    #     active_user = self.env.user
    #     r = self.env['account.analytic.tag'].search([('branch_id', '=', self.branch_id.id)])
    #     line_vals = []
    #     line_vals.append((0, 0, {
    #         'product_id': self.product_id.id,
    #         'name': self.product_id.name,
    #         'account_analytic_id': self.analytical_account_id.id,
    #         'product_qty': 1.0,
    #         'price_unit': 0,
    #         'analytic_tag_ids': r,
    #     }))
    #     po = {
    #         'order_line': line_vals,
    #         'partner_id': active_user.id,
    #         'picking_type_id': '1',
    #         'branch_id': self.branch_id.id,
    #         'fleet_vehicle_id': self.id,
    #     }
    #     record = self.env['purchase.order'].create(po)
    #     self.button_show = True

    def get_purchase_orders(self):
        return {
            'name': _('Requests for Quotation'),
            'domain': [('fleet_vehicle_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'purchase.order',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }


class AnalyticalAccountVehicle(models.Model):
    _inherit = "account.analytic.account"

    fleet_vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")


class FleetContractField(models.Model):
    _inherit = "fleet.vehicle.log.contract"

    partner_id = fields.Many2one('res.partner', string="Customer", tracking=True,
                                 domain=[('partner_type', '=', 'is_customer')])

    rental_id = fields.Many2one('rental.progress', string="Source", tracking=True)


class FleetOdometerField(models.Model):
    _inherit = "fleet.vehicle.odometer"

    value = fields.Integer('Odometer Value', group_operator="max")
    driven = fields.Integer(string="Driven", tracking=True)


class FleetModelField(models.Model):
    _inherit = "fleet.vehicle.model"

    model_year = fields.Selection(selection=[(f'{i}', i) for i in range(1900, 3000)], string='Model Year')
    power_cc = fields.Char(string="Power/CC")

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s : %s: %s : %s' % (rec.brand_id.name, rec.name, rec.model_year, rec.power_cc)))
        return res
