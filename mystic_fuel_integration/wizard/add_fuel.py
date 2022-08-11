from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError


class FuelWizard(models.Model):
    _name = "addfuel.wizard"
    _description = "Add Fuel Wizard"

    entry_type = fields.Selection([
        ('card', 'Card'),
        ('slip', 'Slip'),
    ], 'Entry Type')
    payment_mode = fields.Selection([
        ("own_account", "Employee (to reimburse)"),
        ("company_account", "Company")
    ], tracking=True, string="Paid By")

    description = fields.Char(string='Description')
    date = fields.Date(string="Date", tracking=True)
    ref_no = fields.Char(string='Ref#')
    vendor_id = fields.Many2one('res.partner', string="Vendor", tracking=True,
                                domain=[('partner_type', '=', 'is_pump')])
    km_in = fields.Integer(string='Km In')
    km_out = fields.Integer(string='Km Out')
    qty = fields.Float(string='Qty')
    rate = fields.Float(string='Rate')

    def add_fuel_button(self):
        result = self.env['fuel.management'].browse(self.env.context.get('active_ids'))

        diff = 0
        diff = self.km_in - self.km_out
        print(self.km_out)
        self.env['fuel.lines'].create({
            'date': self.date,
            'description': self.description,
            'entry_type': self.entry_type,
            'ref_no': self.ref_no,
            'km_in': self.km_in,
            'km_out': self.km_out,
            'diff': diff,
            'qty': self.qty,
            'rate': self.rate,
            'mpg': diff/self.qty,
            'amount': self.rate * self.qty,
            'rs_per_km': (self.rate * self.qty) / diff,
            'vendor_id': self.vendor_id.id,
            'payment_mode': self.payment_mode,
            'fuel_id': result.id,
        })
        # if self.entry_type == 'card':
        #     print("card")
        #     self.env['account.move'].create({
        #         'date': self.date,
        #         'description': self.description,
        #         'ref_no': self.ref_no,
        #         'km_in': self.km_in,
        #         'km_out': self.km_out,
        #         'diff': diff,
        #         'qty': self.qty,
        #         'rate': self.rate,
        #         'mpg': diff/self.qty,
        #         'amount': self.rate * self.qty,
        #         'rs_per_km': (self.rate * self.qty) / diff,
        #         'vendor_id': self.vendor_id.id,
        #         'payment_mode': self.payment_mode,
        #         'fuel_id': result.id,
        #     })
        # elif self.entry_type == 'slip':
        #     print("slip")


