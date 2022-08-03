from odoo import models, fields


class GustedHolidays(models.Model):
    _name = 'hr.gusted.holidays'
    _rec_name = 'title'

    title = fields.Char('Title')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')