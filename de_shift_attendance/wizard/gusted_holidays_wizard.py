from odoo import models, fields, api, _


class GustedHolidaysWizard(models.TransientModel):
    _name = 'gusted.holiday.wizard'

    title = fields.Char('Title')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    gusted_holidays_id = fields.Many2one('hr.gusted.holidays')

    def action_set_holidays(self):
        for rec in self:
            lines_records = self.env['hr.shift.management.line'].search(
                [('date', '>=', rec.date_from), ('date', '<=', rec.date_to)])
            for line in lines_records:
                line.rest_day = True

            gusted_holidays = {
                'title': rec.title,
                'date_from': rec.date_from,
                'date_to': rec.date_to
            }
            record = self.env['hr.gusted.holidays'].create(gusted_holidays)
