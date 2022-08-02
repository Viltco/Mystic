from odoo import models, api
from datetime import timedelta, datetime


class EmpReport(models.AbstractModel):
    _name = 'report.chauffeur_reporting.chauffeur_report_id_print'
    _description = 'Chauffeur Information Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        result = self.env['chauffeur.info'].browse(self.env.context.get('active_ids'))
        # print(result.department_id.name)
        data = self.env['hr.employee'].search([('branch_id','=',result.branch_id.id),('is_driver','=',True)])
        print(data)
        return {
            'doc_ids': docids,
            'doc_model': 'chauffeur.info',
            'data': data,
        }


