from odoo import models, fields, api


class ContactCreation(models.Model):
    _inherit = "hr.employee"

    is_driver = fields.Boolean(string='Driver')
    # is_create = fields.Boolean()

    @api.model
    def create(self, vals):
        result = super(ContactCreation, self).create(vals)
        record = self.env['res.partner'].search([('name', '=', result.name)])
        if record:
            print('u click')
        if not record:
            res = self.env['res.partner'].create(
                {'name': vals['name'],
                 'phone': vals['mobile_phone'],
                 'partner_type': 'is_driver'
                 })

        return result

