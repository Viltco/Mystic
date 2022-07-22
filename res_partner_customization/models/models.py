from odoo import models, fields, api , _


class AddFieldsPartners(models.Model):
    _inherit = "res.partner"

    # is_customer = fields.Boolean(string='Is Customer')
    # is_vendor = fields.Boolean(string='Is Vendor')
    # is_driver = fields.Boolean(string='Is Driver')

    partner_type = fields.Selection([
        ('is_customer', 'Customer'),
        ('is_vendor', 'Vendor'),
        ('is_driver', 'Driver'), ('is_user', 'User')], default='is_user', string="Partner Type")
    strn = fields.Char(string="STRN", tracking=True)
    ntn = fields.Char(string="NTN/CNIC", tracking=True)
    una = fields.Char(string="UNA", tracking=True)
    _sql_constraints = [
        ('ntn_unique', 'unique(ntn)', 'Cant be duplicate value For NTN!')]

    def action_view_sale_order(self):
        pass

    @api.model
    def create(self, vals):
        result = super(AddFieldsPartners, self).create(vals)
        if result.partner_type == 'is_driver':
            record = self.env['hr.employee'].search([('name' ,'=', result.name)])
            if record:
                print('record')
            if not record:
                res = self.env['hr.employee'].create(
                    {'name': result.name,
                     'mobile_phone': result.phone,
                     'is_driver': True,
                     })
        elif result.partner_type == 'is_customer':
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
