# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from datetime import date


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    lease_bill_id = fields.Many2one('lease.bill', string='Lease Bill')