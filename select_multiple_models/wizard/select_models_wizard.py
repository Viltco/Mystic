# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api


# class AccountMove(models.Model):
#     _inherit = "product.template"
#
#     quantity = fields.Integer(string='Qty')


class SelectModels(models.TransientModel):
    _name = 'select.models'
    _description = 'Select Models'

    model_ids = fields.Many2many('fleet.vehicle.model', string='Models')
    # flag_order = fields.Char('Flag Order')

    def select_models(self):
        contract_id = self.env['res.contract'].browse(self._context.get('active_id', False))
        for model in self.model_ids:
            self.env['contract.lines'].create({
                'model_id': model.id,
                'contract_id': contract_id.id,
            })
