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
        related="employee_id.employee_shift_hours", store=True, string='Shift hours')
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
    employee_deduction = fields.Float()
    loan = fields.Float(readonly=True)
    loan_id = fields.Many2many('employee.loan')
    bonus_id = fields.Many2many('employee.bonus')
    bonus_min = fields.Integer(readonly=True)
    overtime_id = fields.Many2many('employee.overtime')
    overtime_min = fields.Integer(readonly=True)
    present_vacation_days = fields.Float(
        compute="employee_net_salary_calc", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        end_of_month = (fields.Date.today()+relativedelta(months=1)
                        ).replace(day=1)-relativedelta(days=1)
        for rec in res:
            employee_loan = self.env['employee.loan'].search(
                [('employee_id', '=', rec.employee_id.id), ('loan_state', '=', 'approved'), ('start_loan_month', '<=', end_of_month)])
            first_day_in_month = fields.Date.today().replace(
                day=1, month=int(rec.month), year=int(rec.year))
            last_day_in_month = fields.Date.today().replace(day=calendar.monthrange(
                int(rec.year), int(rec.month))[1], month=int(rec.month), year=int(rec.year))
            employee_bonus = self.env['employee.bonus'].search(
                [('employee_id', '=', rec.employee_id.id), ('bonus_state', '=', 'approved'), ('bonus_day', '>=', first_day_in_month), ('bonus_day', '<=', last_day_in_month)])
            employee_overtime = self.env['employee.overtime'].search(
                [('employee_id', '=', rec.employee_id.id), ('overtime_state', '=', 'approved'), ('overtime_day', '>=', first_day_in_month), ('overtime_day', '<=', last_day_in_month)])
            if employee_bonus:
                for bonus in employee_bonus:
                    rec.bonus_id = [(4, bonus.id)]
                    rec.bonus_min += bonus.bonus_min
                    bonus.bonus_state = 'done'
            if employee_overtime:
                for overtime in employee_overtime:
                    rec.overtime_id = [(4, overtime.id)]
                    rec.overtime_min += overtime.overtime_min
                    overtime.overtime_state = 'done'
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
            if rec.bonus_min > 0:
                for bonus in rec.bonus_id:
                    bonus.bonus_state = 'approved'
            if rec.overtime_min > 0:
                for overtime in rec.overtime_id:
                    overtime.overtime_state = 'approved'
        return super().unlink()

    @api.depends("employee_id", "month", 'bonus_min', "employee_deduction")
    def employee_net_salary_calc(self):
        for rec in self:
            if rec.employee_id:
                rec.present_vacation_days = 0
                rec.total_worked_hours = 0
                total_worked_hours = 0
                first_day_in_month = datetime(
                    int(rec.year), int(rec.month), 1, 0, 0, 0)
                last_day = calendar.monthrange(
                    int(rec.year), int(rec.month))[1]
                last_day_in_month = datetime(
                    int(rec.year), int(rec.month), last_day, 23, 59, 59)
                my_logs = self.env['employee.attendance.logs'].search(
                    [('employee_id', '=', rec.employee_id.id), ('in_time', '>=', first_day_in_month), ('in_time', '<=', last_day_in_month)])
                week_end_days = [
                    int(k) for k, v in rec.employee_id.weekend.items() if v]
                hour_price = rec.basic_salary / 30 / rec.employee_shift_hours
                for log in my_logs:
                    total_worked_hours += int(
                        log.salary_hours) + (((log.salary_hours-int(log.salary_hours))*100)/60)
                    rec.total_worked_hours += log.worked_hours
                    if log.is_weekend:
                        rec.present_vacation_days += 1
                total_worked_hours += (len(week_end_days) *
                                       4*rec.employee_shift_hours)+(rec.bonus_min/60)+(rec.overtime_min*1.5/60)
                rec.net_salary = total_worked_hours * \
                    hour_price - rec.employee_deduction - rec.loan

            else:
                rec.present_vacation_days = 0

    def generate_all_payrolls(self):
        records = self.env["employee"].search([])
        for rec in records:
            if not self.env["employee.payroll"].search([("employee_id", "=", rec.id), ("year", "=", fields.Date.today().year), ("month", "=", fields.Date.today().month)]):
                self.env["employee.payroll"].sudo().create(
                    {
                        "employee_id": rec.id,
                    }
                )

    def unlink_all_payrolls(self):
        records = self.env["employee.payroll"].search(
            [('month', '=', fields.Date.today().month), ('year', '=', fields.Date.today().year)])
        if records:
            records.sudo().unlink()
