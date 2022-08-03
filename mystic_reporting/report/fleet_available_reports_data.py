from odoo import models, api
from datetime import timedelta, datetime


class EmpReport(models.AbstractModel):
    _name = 'report.mystic_reporting.fleet_available_id_print'
    _description = 'Fleet Available Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        vehicle_list = []
        data = self.env['fleet.vehicle'].search([])
        print(data)
        if data:
            for re in data:
                if re.state_id.sequence in [0]:
                    print(re)
                    vehicle_list.append({
                        'model_id': re.model_id.name,
                        'license_plate': re.license_plate,
                        'vin_sn': re.vin_sn,
                        'fuel_type': re.fuel_type,
                    })
        # else:
        #     vehicle_list = []
        print(vehicle_list)
        return {
            'docs': docids,
            'doc_model': 'fleet.vehicle',
            'vehicle_list': vehicle_list,
            # 'result': result,
        }


