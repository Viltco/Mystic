from odoo import models, fields, api , _
from odoo.osv import expression


class AddFieldsPartners(models.Model):
    _inherit = "res.partner"

    # is_customer = fields.Boolean(string='Is Customer')
    # is_vendor = fields.Boolean(string='Is Vendor')
    # is_driver = fields.Boolean(string='Is Driver')
    pin_code = fields.Char(string="Pin Code", tracking=True)
    partner_type = fields.Selection([
        ('is_customer', 'Customer'),
        ('is_vendor', 'Vendor'),
        ('is_driver', 'Driver'), ('is_user', 'User')], default='is_user', string="Partner Type")
    strn = fields.Char(string="STRN", tracking=True)
    ntn = fields.Char(string="NTN/CNIC", tracking=True)
    uan = fields.Char(string="UAN", tracking=True)
    _sql_constraints = [
        ('ntn_unique', 'unique(ntn)', 'Cant be duplicate value For NTN!')]

    def action_view_sale_order(self):
        pass

    def name_get(self):
            print('gggg')
            res = []
            for rec in self:
                if rec.partner_type == 'is_driver':
                    res.append((rec.id, '%s-%s' % (rec.name, rec.pin_code)))
                else:
                    res.append((rec.id, '%s' % (rec.name)))
            return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('pin_code', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    @api.model
    def create(self, vals):
        result = super(AddFieldsPartners, self).create(vals)
        if result.partner_type == 'is_customer':
            res = self.env['res.contract'].create(
                {'branch_id': result.branch_id.id,
                 'partner_id': result.id,
                 })
        return result

    # @api.model
    # def create(self, vals):
    #     result = super(AddFieldsPartners, self).create(vals)
    #     if result.partner_type == 'is_customer':
    #         res = self.env['res.contract'].create(
    #             {'branch_id': result.branch_id.id,
    #              'partner_id': result.id,
    #              })
    #     return result

    # def write(self, vals):
    #     result = super(AddFieldsPartners, self).write(vals)
    #     if self.partner_type == 'is_customer':
    #         print("u click")
    #         res = self.env['res.contract'].create(
    #             {'branch_id': self.branch_id.id,
    #              'partner_id': self.id,
    #              })
    #     return result

    def contract_button(self):
        return {
            'name': _('Customer Contracts'),
            'domain': [('partner_id', '=', self.id)],
            'res_model': 'res.contract',
            'view_id': False,
            'context': {
                'active_model': 'res.contract',
                'active_ids': self.ids,
                'default_branch_id': self.branch_id.id,
                'default_partner_id': self.id,
            },
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    contract_counter = fields.Integer(compute='get_contract_counter')

    def get_contract_counter(self):
        for rec in self:
            count = self.env['res.contract'].search_count([('partner_id', '=', self.id)])
            rec.contract_counter = count

#
# class DriverEmployee(models.Model):
#     _inherit = "hr.employee"
#
#     partner_id = fields.Many2one('res.partner', string="Related Partner", tracking=True)
#     nic_issuence_date = fields.Date(string="NIC Issuance Date", tracking=True)
#     nic_expiry_date = fields.Char(string="Expiry Date", tracking=True)
#     license_type = fields.Selection([
#         # ('is_customer', 'Customer'),
#         # ('is_vendor', 'Vendor'),
#         # ('is_driver', 'Driver')
#         ], string="Licenss Type")
#     license_issuence_date = fields.Date(string="License Issuance Date", tracking=True)
#     license_expiry_date = fields.Char(string="License Expiry Date", tracking=True)
#     pin_code = fields.Char(string="Pin Code", tracking=True)
#     pin_code = fields.Char(string="Pin Code", tracking=True)
#
#
#     @api.model
#     def create(self, vals):
#         result = super(DriverEmployee, self).create(vals)
#         if result.is_driver:
#             res = self.env['res.partner'].create(
#                 {'branch_id': result.branch_id.id,
#                  'name': result.name,
#                  'pin_code': result.pin,
#                  'partner_type': 'is_driver',
#                  })
#             print(res)
#             result.partner_id = res.id
#         return result
