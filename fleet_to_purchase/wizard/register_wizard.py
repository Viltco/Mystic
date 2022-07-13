from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RegisterWizard(models.TransientModel):
    _name = "register.wizard"
    _description = "Register Wizard"

    # license_plate = fields.Char(string='License Plate')
    # car_counter_id = fields.Many2one('cars.counter', string="Cars")
    register_lines_id = fields.One2many('car.tree', 'register_id',
                                   string='Lines')

    def register_action(self):
        print("u click")
        for r in self.register_lines_id:
            l = r.license_plate
            r.car_counter_id.vehicle_id.license_plate = l
            r.car_counter_id.vehicle_id.counter = ''
            name = r.car_counter_id.analytical_account_id.name
            t = r.car_counter_id.product_id.name
            sp = name.split('/')
            sp.pop()
            sp = '/'.join(sp)
            sp = sp + f'/{l}'

            p = t.split('/')
            p.pop()
            p = '/'.join(p)
            p = p + f'/{l}'
            print(sp)
            r.car_counter_id.analytical_account_id.update({
                    'name': sp,
                })
            r.car_counter_id.product_id.update({
                'name': p,
            })
            r.car_counter_id.vehicle_id.active= True


            # r.car_counter_id.product_id.name = r.license_plate
            # r.car_counter_id.product_id.product_tmpl_id.name = r.license_plate
        # print(self.vehicle_id.license_plate)
        # print('hhh')
        # self.vehicle_id.product_id.name = self.license_plate
        # self.vehicle_id.analytical_account_id.name = self.license_plate
        # rec.button_show = True
        # self.vehicle_id.active = True










