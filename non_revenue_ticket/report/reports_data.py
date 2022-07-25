from odoo import models, api
from datetime import timedelta, datetime


class EmpReport(models.AbstractModel):
    _name = 'report.non_revenue_ticket.nrt_report_id_print'
    _description = 'NRT Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        result = self.env['nrt.report'].browse(self.env.context.get('active_ids'))
        data = self.env['nonrevenue.ticket'].search([('created_on', '>=', result.date_from),('created_on', '<=', result.date_to)])
        print(data)
        return {
            'doc_ids': docids,
            'doc_model': 'bonus.report',
            'date_wizard': result,
            'data': data,
        }

    # hr.contract(75, 76, 77, 78, 79, 80, 180, 190, 198)

