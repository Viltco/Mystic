from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ChauffeurInWizard(models.TransientModel):
    _name = "chauffeur.in"
    _description = "Chauffeur In Wizard"

    km_in = fields.Integer(string="Kms In", tracking=True)
    time_in = fields.Datetime('Time In')

    def chauffeur_in_action(self):
        print("u click")
        for rec in self:
            record = self.env['rental.progress'].browse(self.env.context.get('active_id'))
            if rec.km_in > record.km_out:
                record.km_in = rec.km_in
                record.time_in = rec.time_in
                record.state = 'chauffeur_in'
                result = self.env['res.contract'].search(
                    [('partner_id', '=', record.name.id),('state', '=', 'confirm')])
                i = 0
                for r in result.contract_lines_id:
                    if r.model_id.id == record.vehicle_no.model_id.id:
                        if r.model_id.model_year == record.vehicle_no.model_id.model_year:
                            if record.based_on == 'daily':
                                i = r.per_day_rate
                            elif record.based_on == 'weekly':
                                i = r.per_week_rate
                            elif record.based_on == 'monthly':
                                i = r.per_month_rate
                            vals = {
                                'partner_id': record.name.id,
                                'vehicle_id': record.vehicle_no.id,
                                'rental_id': record.id,
                                'start_date': record.time_out,
                                'expiration_date': rec.time_in,
                                'cost_frequency': record.based_on,
                                'cost_generated': i,
                                # 'reservation_id': self.id,
                            }
                            self.env['fleet.vehicle.log.contract'].create(vals)
            else:
                raise ValidationError(f'Please enter value greater than KM Out')

    # for rec in self:
    #     if rec.km_in > rec.km_out:
    #         rec.state = 'chauffeur_in'
    #     elif rec.km_in < rec.km_out:
    #         raise ValidationError(f'Please enter value greater than KM Out')



