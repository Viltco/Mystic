# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from datetime import date
from lxml import etree


class FleetVehicleTrk(models.Model):
    _inherit = 'fleet.vehicle'

    tracking_charges_lines = fields.One2many('tracking.charges.line', 'tracking_charge_id')

    active = fields.Boolean('Active', default=True)

    def toggle_active(self):
        for record in self.tracking_charges_lines:
            record.tracking_status = 'inactive'
        res = super(FleetVehicleTrk, self).toggle_active()
        return res


class TrackingChargesLines(models.Model):
    _name = 'tracking.charges.line'
    _description = 'Tracking Charges Lines'
    _rec_name = 'date_from'

    tracking_charge_id = fields.Many2one('fleet.vehicle')
    active = fields.Boolean('Active', default=True)

    # @api.depends('tracking_charge_id')
    # def default_branch_id(self):
    #     return self.tracking_charge_id.branch_id.id

    # branch_id = fields.Many2one('res.branch', string='Branch', default=default_branch_id)
    branch_id = fields.Many2one('res.branch', string='Branch', compute='_compute_branch_id')
    # branch_id = fields.Many2one('res.branch', string='Branch', default=lambda self: [self.tracking_charge_id.branch_id.id])

    @api.depends('tracking_charge_id')
    def _compute_branch_id(self):
        for rec in self:
            if rec.tracking_charge_id.branch_id:
                rec.branch_id = rec.tracking_charge_id.branch_id.id
            else:
                rec.branch_id = []

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='Date To')
    re_amount = fields.Float(string='Revalued Amount')
    percentage = fields.Float(string='Percentage %')
    amount_subtotal = fields.Float(string='Amount', compute='_compute_amount_subtotal')
    tracking_status = fields.Selection([
        ('inactive', 'InActive'),
        ('active', 'Active'),
    ], string='Tracking Status', default='active')

    @api.depends('re_amount', 'percentage')
    def _compute_amount_subtotal(self):
        for record in self:
            if record:
                record.amount_subtotal = (record.re_amount * record.percentage) / 100
            else:
                record.amount_subtotal = 0

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(TrackingChargesLines, self).fields_view_get(
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
        selected_records = self.env['tracking.charges.line'].browse(selected_ids)
        for rec in selected_records:
            val_list.append(rec.id)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Tracking Charges',
            'view_id': self.env.ref('mystic_tracking_charges.view_tracking_wizard_form', False).id,
            'context': {
                'default_fleet_ids': val_list,
            },
            'target': 'new',
            'res_model': 'tracking.wizard',
            'view_mode': 'form',
        }
