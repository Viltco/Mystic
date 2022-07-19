from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class PurchaseCars(models.Model):
    _name = "po.cars"
    _description = "Car"
    _rec_name = 'number'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    model_id = fields.Many2one('fleet.vehicle.model', string="Model", tracking=True)
    # branch_id = fields.Many2one('res.branch', string="Branch", tracking=True, required=True)
    number = fields.Char(string='Number', required=True, copy=False, readonly=True, default='New')
    # analytical_account_id = fields.Many2one('account.analytic.account', string="Analytical Account")
    # product_id = fields.Many2one('product.product', string="Product")
    # vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", tracking=True, copy=False)
    button_show = fields.Boolean(default=False)
    button_po_show = fields.Boolean(default=False)
    pbo = fields.Char(string='PBO')
    loan_number = fields.Char(string='Loan No')
    qty = fields.Integer(string='Quantity', required=True)

    stage_id = fields.Selection([
        ('purchase', 'PURCHASED'),
        ('not_purchase', 'NOT PURCHASED')], default='not_purchase', string="Stage ID")

    @api.model
    def create(self, values):
        values['number'] = self.env['ir.sequence'].next_by_code('po.cars') or _('New')
        for i in range(values['qty']):
            v = self.env['fleet.vehicle.model'].browse([values['model_id']])
            print(v)
            print(f"'model_id': {str(values['model_id'])}/{str(values['number'])}")
            rest = self.env['fleet.vehicle'].create(
                # {'model_id': values['model_id'],
                {
                    'name': str(v.name) + '/' + str(v.brand_id.name) + '/' + str(v.model_year) + '/' + str(
                        v.power_cc) + '/' + str(values['number']),
                    'model_id': values['model_id'],
                    # 'branch_id': values['branch_id'],
                    'active': False,
                })
            print({'name': str(v.name) + '/' + str(v.brand_id.name) + '/' + str(v.model_year) + '/' + str(
                        v.power_cc) + '/' + str(values['number']),
                    'model_id': values['model_id']})
            # values['vehicle_id'] = res.id
            resul = self.env['account.analytic.account'].create(
                {'name': str(v.name) + '/' + str(v.brand_id.name) + '/' + str(v.model_year) + '/' + str(
                    v.power_cc) + '/' + str(values['number']),
                 'fleet_vehicle_id': rest.id,
                 })
            # values['analytical_account_id'] = resul.id
            # r = self.env['product.category'].search([('name', '=', 'Pool Vehicles')])
            r = self.env['ir.config_parameter'].get_param('fleet_to_purchase.product_category_id')
            print(r, "Product Category")
            resu = self.env['product.product'].create(
                {'name': str(v.name) + '/' + str(v.brand_id.name) + '/' + str(v.model_year) + '/' + str(
                    v.power_cc) + '/' + str(values['number']),
                 'fleet_vehicle_id': rest.id,
                 # 'branch_ids': res['branch_id'],
                 'type': 'product',
                 'categ_id': r,
                 'invoice_policy': 'order',
                 'purchase_method': 'purchase',
                 })
            # values['product_id'] = resu.id
            resu.product_tmpl_id.write({'fleet_vehicle_id': rest.id})

            res = self.env['cars.counter'].create(
                {'number': values['number'],
                 'analytical_account_id': resul.id,
                 'product_id': resu.id,
                 'vehicle_id': rest.id,
                 })
            rest.update({
                'analytical_account_id': resul.id,
                'product_id': resu.id,
                'counter': res.counter,
            })
            resul.update({
                'name': str(v.name) + '/' + str(v.brand_id.name) + '/' + str(v.model_year) + '/' + str(
                    v.power_cc) + '/' + res.counter
            })
            resu.update({
                'name': str(v.name) + '/' + str(v.brand_id.name) + '/' + str(v.model_year) + '/' + str(
                    v.power_cc) + '/' + res.counter
            })
            # values['vehicle_id'] = res.id
        return super(PurchaseCars, self).create(values)

    def action_register(self):
        record = self.env['cars.counter'].search(
            [('number', '=', self.number), ('vehicle_id.license_plate', '=', False)])
        car_list = []
        for r in record:
            car_list.append((0, 0, {
                'car_counter_id': r.id,
                'license_plate': '',
            }))
        print(car_list)
        if not car_list:
            self.button_show = True
        return {
            'name': _('Register'),
            'res_model': 'register.wizard',
            'view_mode': 'form',
            'context': {
                'active_model': 'po.cars',
                'active_ids': self.ids,
                'default_register_lines_id': car_list,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_counter_view(self):
        return {
            'name': _('Cars'),
            'domain': [('number', '=', self.number)],
            'view_type': 'form',
            'res_model': 'cars.counter',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    vehicles_count = fields.Integer(string='Vehicle', compute='get_vehicle_counter')

    def get_vehicle_counter(self):
        for rec in self:
            count = self.env['cars.counter'].search_count([('number', '=', self.number)])
            rec.vehicles_count = count

    # def action_server_invoice(self):
    #     active_user = self.env.user
    #     record = self.env['cars.counter'].search([('number', '=', self.number)])
    #     line_vals = []
    #     for r in record:
    #         line_vals.append((0, 0, {
    #             'product_id': r.product_id.id,
    #             'name': r.product_id.name,
    #             'account_analytic_id': r.analytical_account_id.id,
    #             'product_qty': 1.0,
    #             'price_unit': 0,
    #             # 'analytic_tag_ids': r,
    #         }))
    #     po = {
    #         'order_line': line_vals,
    #         'partner_id': active_user.id,
    #         'picking_type_id': '1',
    #         # 'branch_id': self.branch_id.id,
    #         # 'fleet_vehicle_id': self.vehicle_id.id,
    #     }
    #     record = self.env['purchase.order'].create(po)

    def action_server_multiple_invoice(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['po.cars'].browse(selected_ids)
        line_vals = []
        active_user = self.env.user
        if len(selected_records) <= 1:
            for a in self:
                record = self.env['cars.counter'].search([('number', '=', a.number)])
                for r in record:
                    line_vals.append((0, 0, {
                        'product_id': r.product_id.id,
                        'name': r.product_id.name,
                        'account_analytic_id': r.analytical_account_id.id,
                        'product_qty': 1.0,
                        'price_unit': 0,
                        # 'analytic_tag_ids': r,
                    }))
                # raise ValidationError("Please select multiple Rentals to merge in the list view.... ")
        else:
            for r in selected_records:
                record = self.env['cars.counter'].search([('number', '=', r.number)])
                # print(record)
                for r in record:
                    # print(r.product_id.name)
                    line_vals.append((0, 0, {
                        'product_id': r.product_id.id,
                        'name': r.product_id.name,
                        'account_analytic_id': r.analytical_account_id.id,
                        'product_qty': 1.0,
                        'price_unit': 0,
                        # 'analytic_tag_ids': r,
                    }))
        print(line_vals)
        purchase_obj = self.env['purchase.order']
        vals = {
            'order_line': line_vals,
            'partner_id': active_user.id,
            'car_to_purchase_ids': selected_records.ids,
            'picking_type_id': '1',
            # 'branch_id': self.branch_id.id,
            # 'fleet_vehicle_id': self.vehicle_id.id,
        }
        self.write({
            'stage_id': 'purchase'
        })
        ac = purchase_obj.create(vals)

    purchase_count = fields.Integer(compute='get_purchase_count')

    def get_purchase_count(self):
        for rec in self:
            count = self.env['purchase.order'].search_count([('car_to_purchase_ids', '=', self.id)])
            rec.purchase_count = count

    def action_purchase_car_view(self):
        return {
            'name': _('Purchase Order'),
            'domain': [('car_to_purchase_ids', '=', self.id)],
            'view_type': 'form',
            'res_model': 'purchase.order',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
