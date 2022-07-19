# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from datetime import date
from lxml import etree


class FleetVehicleInh(models.Model):
    _inherit = 'fleet.vehicle'

    fleet_insurance_lines = fields.One2many('fleet.insurance.line', 'fleet_vehicle_id')


class FleetInsuranceLines(models.Model):
    _name = 'fleet.insurance.line'
    _description = 'Fleet Insurance Line'
    _rec_name = 'date_from'

    fleet_vehicle_id = fields.Many2one('fleet.vehicle')

    # def default_branch_id(self):
    #     return self.fleet_vehicle_id.branch_id.id

    # branch_id = fields.Many2one('res.branch', string='Branch', default=default_branch_id)

    branch_id = fields.Many2one('res.branch', string='Branch', compute='_compute_branch_id')

    @api.depends('fleet_vehicle_id')
    def _compute_branch_id(self):
        if self.fleet_vehicle_id.branch_id:
            self.branch_id = self.fleet_vehicle_id.branch_id.id
        else:
            self.branch_id = []

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='Date To')
    re_amount = fields.Float(string='Revalued Amount')
    percentage = fields.Float(string='Percentage %')
    amount_subtotal = fields.Float(string='Amount', compute='_compute_amount_subtotal')
    insurance_status = fields.Selection([
        ('inactive', 'InActive'),
        ('active', 'Active'),
    ], string='Insurance Status', default='active')

    @api.depends('re_amount', 'percentage')
    def _compute_amount_subtotal(self):
        for record in self:
            if record:
                record.amount_subtotal = (record.re_amount * record.percentage) / 100
            else:
                record.amount_subtotal = 0

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(FleetInsuranceLines, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        temp = etree.fromstring(result['arch'])
        temp.set('create', '0')
        temp.set('edit', '0')
        temp.set('delete', '0')
        result['arch'] = etree.tostring(temp)
        return result

    def action_create_bill_wizard(self):
        val_list = []
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['fleet.insurance.line'].browse(selected_ids)
        for rec in selected_records:
            val_list.append(rec.id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Insurance Bills',
            'view_id': self.env.ref('mystic_insurance.view_insurance_wizard_form', False).id,
            'context': {
                'default_fleet_ids': val_list,
            },
            'target': 'new',
            'res_model': 'insurance.wizard',
            'view_mode': 'form',
        }
