from odoo import models, fields
from odoo.exceptions import UserError
from datetime import datetime
from calendar import monthrange


class HrPayslipInh(models.Model):
    _inherit = 'hr.payslip'

    rental_allowance = fields.Float()
    osa = fields.Float()
    local_night = fields.Float()
    out_night = fields.Float()
    raksha = fields.Float()
    ogh = fields.Float()
    # overtime = fields.Float()
    shorttime = fields.Float()
    extratime = fields.Float()
    month_days = fields.Float()

    def current_month_days(self):
        num_days = monthrange(self.date_from.year, self.date_from.month)[1]
        self.month_days = num_days

    def get_overtime_minutes(self, overtime):
        result = '{0:02.0f}:{1:02.0f}'.format(*divmod(overtime * 60, 60))
        # print(type(result))
        time = datetime.strptime(result, '%H:%M')
        overtime_minutes = (time.time().hour * 60) + time.time().minute
        return overtime_minutes

    def get_shift_minutes(self):
        roaster = self.env['hr.shift.management.line'].search(
            [('rel_management.employee_id', '=', self.employee_id.id), ('date', '=', self.date_from)])
        result = '{0:02.0f}:{1:02.0f}'.format(*divmod(roaster.shift_one.shift_duration * 60, 60))
        time = datetime.strptime(result, '%H:%M')
        shift_minutes = (time.time().hour * 60) + time.time().minute
        return shift_minutes

    def per_minute_wage_rate(self):
        roaster = self.env['hr.shift.management.line'].search(
            [('rel_management.employee_id', '=', self.employee_id.id), ('date', '=', self.date_from)])
        result = '{0:02.0f}:{1:02.0f}'.format(*divmod(roaster.shift_one.shift_duration * 60, 60))
        time = datetime.strptime(result, '%H:%M')
        # shift_minutes = (time.time().hour * 60) + time.time().minute
        rate = ((self.contract_id.wage/self.month_days)/time.time().hour)/60
        print(rate)
        return rate

    def get_allowances(self):
        self.current_month_days()
        attendances = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id)])
        att_list = []
        for rec in attendances:
            if rec.check_in.date() >= self.date_from and rec.check_in.date() <= self.date_to:
                att_list.append(rec.id)

        att = self.env['hr.attendance'].browse(att_list)
        rental_allowance = 0
        osa = 0
        local_night = 0
        out_night = 0
        raksha = 0
        ogh = 0
        # overtime = 0
        shorttime = 0
        extratime = 0
        for i in att:
            rental_allowance = rental_allowance + i.rental_count
            osa = osa + i.osa_count
            local_night = local_night + i.loc_night_count
            out_night = out_night + i.out_night_count
            raksha = raksha + i.rakhsha_count
            ogh = ogh + i.rest_day

            # overtime = overtime + i.overtime
            shorttime = shorttime + i.short_time
            extratime = extratime + i.extra_time

        shift_minutes = self.get_shift_minutes()
        per_minute_rate = self.per_minute_wage_rate()
        if shorttime > 0 or extratime > 0:
            # overtime_minutes = self.get_overtime_minutes(overtime)
            shorttime_minutes = self.get_overtime_minutes(shorttime)
            extratime_minutes = self.get_overtime_minutes(extratime)
        else:
            # overtime_minutes = 0
            shorttime_minutes = 0
            extratime_minutes = 0
        # self.overtime = overtime_minutes * per_minute_rate
        self.shorttime = shorttime_minutes * per_minute_rate
        self.extratime = extratime_minutes * per_minute_rate
        rates = self.env['allowance.rates'].search([], limit=1)
        if rates:
            self.rental_allowance = rental_allowance * rates.rentals
            self.osa = osa * rates.out_station
            self.local_night = local_night * rates.local_night
            self.out_night = out_night * rates.out_night
            self.raksha = raksha * rates.rakhsha
            self.ogh = ogh * rates.over_days

        # print(attendances)

    def compute_sheet(self):
        for rec in self:
            rec.get_allowances()
            # # Loans
            # loan = self.env['hr.loan'].search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'approve'),
            #                                    ('is_payment_created', '=', True)])
            # amount = 0
            # if loan and loan.move_id.state == 'posted':
            #     for line in loan.loan_lines:
            #         if rec.date_from.month == line.date.month and line.status != 'paid':
            #             amount = amount + line.amount
            #             rec.loan_line = line.id
            # rec.loan_amount = amount

            return super(HrPayslipInh, self).compute_sheet()

    def action_payslip_done(self):
        record = super(HrPayslipInh, self).action_payslip_done()
        self._action_general_entry()

    def _action_general_entry(self):
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        for rec in self:
            move_dict = {
                'ref': rec.number,
                'journal_id': rec.journal_id.id,
                'branch_id': rec.employee_id.branch_id.id,
                # 'address_id': rec.address_id.id,
                # 'partner_id': rec.employee_id.address_home_id.id,
                'date': datetime.today(),
                'state': 'draft',
            }
            for oline in rec.line_ids:
                if oline.salary_rule_id.account_debit and oline.salary_rule_id.account_credit and oline.total > 0:
                    debit_line = (0, 0, {
                        'name': oline.name,
                        'branch_id': rec.contract_id.branch_id.id,
                        'analytic_tag_ids': [rec.contract_id.analytical_tag_id.id],
                        'debit': abs(oline.total),
                        'credit': 0.0,
                        'partner_id': rec.employee_id.address_home_id.id,
                        'account_id': oline.salary_rule_id.account_debit.id,
                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
                    credit_line = (0, 0, {
                        'name': oline.name,
                        'branch_id': rec.contract_id.branch_id.id,
                        'analytic_tag_ids': [rec.contract_id.analytical_tag_id.id],
                        'debit': 0.0,
                        'partner_id': rec.employee_id.address_home_id.id,
                        'credit': abs(oline.total),
                        'account_id': oline.salary_rule_id.account_credit.id,
                    })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            if line_ids:
                print(line_ids)
                move_dict['line_ids'] = line_ids
                move = self.env['account.move'].create(move_dict)
                line_ids = []
                rec.move_id = move.id