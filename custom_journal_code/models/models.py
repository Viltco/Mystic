# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CustomJournalCode(models.Model):
    _inherit = 'account.journal'

    code = fields.Char('Short Code', size=10)
