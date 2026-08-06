from odoo import models, fields, api
import calendar
from dateutil.relativedelta import relativedelta
from datetime import datetime


class Payroll(models.Model):
    _name = "employee.payroll"
    _description = "hr_system_employee_payroll"

    _rec_name = "employee_id"
    employee_id = fields.Many2one("employee")
    employee_shift_hours = fields.Float(
        related="employee_id.employee_shift_hours", store=True
    )
    basic_salary = fields.Float(
        related="employee_id.employee_basic_salary", store=True)
    total_worked_hours = fields.Float(readonly=True)
    month = fields.Selection(
        [
            ("1", "JAN"),
            ("2", "FEB"),
            ("3", "MAR"),
            ("4", "APR"),
            ("5", "MAY"),
            ("6", "JUN"),
            ("7", "JUL"),
            ("8", "AUG"),
            ("9", "SEP"),
            ("10", "OCT"),
            ("11", "NOV"),
            ("12", "DEC"),
        ],
        default=str(fields.Date.today().month),
    )
    year = fields.Char(default=fields.Date.today().year)
    net_salary = fields.Float(compute="employee_net_salary_calc", store=True)
    employee_bonus = fields.Float()
    employee_deduction = fields.Float()
    week_end_day = fields.Integer()
    loan = fields.Float()
    loan_id = fields.Many2many('employee.loan')
    present_vacation = fields.Float(
        compute="employee_net_salary_calc", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        end_of_month = (fields.Date.today()+relativedelta(months=1)
                        ).replace(day=1)-relativedelta(days=1)
        for rec in res:
            employee_loan = self.env['employee.loan'].search(
                [('employee_id', '=', rec.employee_id.id), ('loan_state', '=', 'approved'), ('start_loan_month', '<=', end_of_month)])
            if employee_loan:
                for loan in employee_loan:
                    rec.loan_id = [(4, loan.id)]
                    rec.loan += loan.loan_amount / loan.loan_repayment_period
                    loan.remaining_amount -= loan.loan_amount / loan.loan_repayment_period
                    if loan.remaining_amount == 0:
                        loan.loan_state = 'paid'
        return res

    @api.model
    def unlink(self):
        for rec in self:
            if rec.loan > 0:
                for loan in rec.loan_id:
                    loan.loan_state = 'approved'
                    loan.remaining_amount += loan.loan_amount/loan.loan_repayment_period
        return super().unlink()

    @api.depends("employee_id", "month", "employee_bonus", "employee_deduction")
    def employee_net_salary_calc(self):
        for rec in self:
            if rec.employee_id:
                now = fields.datetime.now()
                rec.present_vacation = 0
                total_worked_hours = 0
                weekend_days = 0
                hour_price = rec.basic_salary / \
                    calendar.monthrange(now.year, now.month)[
                        1]/rec.employee_shift_hours
                first_day_in_month = datetime(now.year, now.month, 1, 0, 0, 0)
                last_day = calendar.monthrange(now.year, now.month)[1]
                last_day_in_month = datetime(
                    now.year, now.month, last_day, 23, 59, 59)
                my_logs = self.env['employee.attendance.logs'].search(
                    [('employee_id', '=', rec.employee_id.id), ('in_time', '>=', first_day_in_month), ('in_time', '<=', last_day_in_month)])
                for log in my_logs:
                    total_worked_hours += int(
                        log.salary_hours) + (((log.salary_hours-int(log.salary_hours))*100)/60)
                    rec.total_worked_hours += log.worked_hours
                    if log.is_weekend:
                        rec.present_vacation += log.salary_hours * hour_price
                rec.net_salary = total_worked_hours * hour_price + \
                    rec.employee_bonus - rec.employee_deduction - rec.loan
                week_end_days = next(
                    (k for k, v in rec.employee_id.weekend.items() if v == True), False)
                if week_end_days:
                    for day in week_end_days:
                        for days in range(
                            1, calendar.monthrange(
                                int(rec.year), int(rec.month))[1] + 1
                        ):
                            if calendar.weekday(
                                int(rec.year), int(rec.month), days
                            ) == int(day):
                                weekend_days += 1
                rec.net_salary += weekend_days * \
                    (rec.employee_id.employee_shift_hours * hour_price)
            else:
                rec.present_vacation = 0

    def generate_all_payrolls(self):
        records = self.env["employee"].search([])
        for rec in records:
            if not self.env["employee.payroll"].search([("employee_id", "=", rec.id), ("year", "=", fields.Date.today().year), ("month", "=", fields.Date.today().month)]):
                self.env["employee.payroll"].create(
                    {
                        "employee_id": rec.id,
                    }
                )

    def unlink_all_payrolls(self):
        records = self.env["employee.payroll"].search(
            [('month', '=', fields.Date.today().month), ('year', '=', fields.Date.today().year)])
        if records:
            records.unlink()
