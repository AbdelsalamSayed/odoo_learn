from odoo import models, fields, api
import calendar


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
    present_vacation = fields.Float(
        compute="employee_net_salary_calc", store=True)

    @api.depends("employee_id", "month", "employee_bonus", "employee_deduction")
    def employee_net_salary_calc(self):
        for rec in self:
            if rec.employee_id:
                worked_hours = 0
                weekend_days = 0
                present_vacation_days = 0
                for day in rec.employee_id.weekend:
                    if rec.employee_id.weekend[day]:
                        for days in range(
                            1, calendar.monthrange(
                                int(rec.year), int(rec.month))[1] + 1
                        ):
                            if calendar.weekday(
                                int(rec.year), int(rec.month), days
                            ) == int(day):
                                weekend_days += 1
                for log in self.env['employee.attendance'].search([('employee_id', '=', rec.employee_id.id)]):
                    if str(log.log_date.month) == rec.month:
                        worked_hours += log.employee_shift_hours
                    if log.is_weekend:
                        present_vacation_days += 1
                hour_price = rec.basic_salary / 30 / rec.employee_shift_hours
                rec.week_end_day = weekend_days
                paid_leave = weekend_days * rec.employee_shift_hours * hour_price
                rec.present_vacation = (
                    hour_price * rec.employee_shift_hours * present_vacation_days
                )
                rec.total_worked_hours = worked_hours
                rec.net_salary = (
                    hour_price * rec.total_worked_hours
                    - rec.employee_deduction
                    + rec.employee_bonus
                    + paid_leave
                )
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
