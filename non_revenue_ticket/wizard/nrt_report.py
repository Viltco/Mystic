from datetime import datetime
from odoo import api, fields, models, _


class NRTReport(models.TransientModel):
    _name = "nrt.report"
    _description = "NRT Report"

    date_from = fields.Datetime('Date From')
    date_to = fields.Datetime('Date To')

    def print_action(self):
        print("u click")
        data = {
            'form': self.read()[0],
        }
        return self.env.ref('non_revenue_ticket.nrt_report_pdf').report_action(self, data=data)




