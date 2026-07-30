from odoo import models, fields, api
import calendar


class Payroll(models.Model):
    _name = 'employee.payroll'
    _description = 'hr_system_employee_payroll'

    _rec_name = 'employee_id'
    employee_id = fields.Many2one('employee')
    employee_shift_hours = fields.Float(
        related='employee_id.employee_shift_hours')
    basic_salary = fields.Float(related='employee_id.employee_basic_salary')
    employee_attendance_logs = fields.One2many(
        'employee.attendance', 'employee_id', related='employee_id.attendance_ids')
    total_worked_hours = fields.Float(readonly=True)
    month = fields.Selection([
        ('1', 'JAN'),
        ('2', 'FEB'),
        ('3', 'MAR'),
        ('4', 'APR'),
        ('5', 'MAY'),
        ('6', 'JUN'),
        ('7', 'JUL'),
        ('8', 'AUG'),
        ('9', 'SEP'),
        ('10', 'OCT'),
        ('11', 'NOV'),
        ('12', 'DEC'),
    ], default=str(fields.Date.today().month))
    year = fields.Char(default=fields.Date.today().year)
    net_salary = fields.Float(
        compute='employee_net_salary_calc', store=True)
    employee_bonus = fields.Float()
    employee_deduction = fields.Float()
    week_end_day = fields.Integer()
    present_vacation = fields.Float(
        compute='employee_net_salary_calc', store=True)

    @api.onchange('employee_id', 'month', 'employee_bonus', 'employee_deduction')
    def employee_net_salary_calc(self):
        for rec in self:
            if rec.employee_id:
                for day in rec.employee_id.weekend:
                    if rec.employee_id.weekend[day]:
                        for days in range(1, calendar.monthrange(int(rec.year), int(rec.month))[1]+1):
                            if calendar.weekday(int(rec.year), int(rec.month), days) == int(day):
                                rec.week_end_day += 1
                rec.total_worked_hours = 0
                for log in rec.employee_attendance_logs:
                    if str(log.log_date.month) == rec.month:
                        rec.total_worked_hours += log.employee_shift_hours
                hour_price = rec.basic_salary / 30 / rec.employee_shift_hours
                rec.present_vacation = hour_price * rec.employee_shift_hours * rec.week_end_day
                print(hour_price)
                print(rec.total_worked_hours)
                print(rec.employee_deduction)
                print(rec.employee_bonus)
                print(rec.employee_shift_hours)
                print(rec.week_end_day)
                rec.net_salary = hour_price * rec.total_worked_hours - rec.employee_deduction + \
                    rec.employee_bonus + rec.present_vacation
            rec.present_vacation = 0
