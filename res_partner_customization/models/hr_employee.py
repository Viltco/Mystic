from odoo import models, fields, api


class ContactCreation(models.Model):
    _inherit = "hr.employee"

    is_driver = fields.Boolean(string='Driver')
    # is_create = fields.Boolean()
    partner_id = fields.Many2one('res.partner', string="Related Partner", tracking=True)
    nic_issuence_date = fields.Date(string="NIC Issuance Date", tracking=True)
    nic_expiry_date = fields.Char(string="NIC Expiry Date", tracking=True)
    license_type = fields.Selection([
        ('motor_car_jeep', 'Motor Car Jeep'),
        ('ltv', 'LTV'),
        ('htv', 'HTV  '),
        ('psv', 'PSV  '),
    ], string="Licenss Type")
    license_issuence_date = fields.Date(string="License Issuance Date", tracking=True)
    license_expiry_date = fields.Char(string="License Expiry Date", tracking=True)
    caste = fields.Char(string="Caste", tracking=True)
    police_verification = fields.Char(string="Police Verification", tracking=True)
    shift_id = fields.Many2one('hr.shift', string="Shifts", tracking=True)


    @api.model
    def create(self, vals):
        result = super(ContactCreation, self).create(vals)
        if result.is_driver:
            res = self.env['res.partner'].create(
                {'branch_id': result.branch_id.id,
                 'name': result.name,
                 'pin_code': result.pin,
                 'partner_type': 'is_driver',
                 })
            print(res)
            result.partner_id = res.id
        return result

    # @api.model
    # def create(self, vals):
    #     result = super(ContactCreation, self).create(vals)
    #     record = self.env['res.partner'].search([('name', '=', result.name)])
    #     if record:
    #         print('u click')
    #     if not record:
    #         res = self.env['res.partner'].create(
    #             {'name': vals['name'],
    #              'phone': vals['mobile_phone'],
    #              'partner_type': 'is_driver'
    #              })
    #
    #     return result

