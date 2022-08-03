from odoo import api, fields, models, _


class ChauffeurInfoReport(models.TransientModel):
    _name = 'chauffeur.info'

    branch_id = fields.Many2one('res.branch',string="Branch")

    def menu_report_action(self):
        data = {
            'form': self.read()[0],
        }
        return self.env.ref('mystic_reporting.chauffeur_report_pdf').report_action(self, data=data)

