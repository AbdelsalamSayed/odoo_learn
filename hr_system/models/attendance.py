from odoo import models, fields, api
from odoo.exceptions import ValidationError
import calendar


class Attendance(models.Model):
    _name = 'employee.attendance'
    _description = 'hr_system_employee_attendance'

    _rec_name = 'employee_id'
    employee_id = fields.Many2one('employee')
    log_date = fields.Date(default=fields.Date.today())
    employee_shift_from = fields.Float(default=8)
    employee_shift_to = fields.Float(default=4)
    employee_shift_hours = fields.Float(
        string='Total hours', compute='_compute_shift_hours')
    employee_shift_from_period = fields.Selection([
        ('am', 'AM'),
        ('pm', 'PM'),
    ], default='am', required=True)
    employee_shift_to_period = fields.Selection([
        ('am', 'AM'),
        ('pm', 'PM'),
    ], default='pm', required=True)
    is_weekend = fields.Boolean(default=False)

    @api.depends('employee_shift_from', 'employee_shift_to', 'employee_shift_from_period', 'employee_shift_to_period')
    def _compute_shift_hours(self):
        for rec in self:
            rec.employee_shift_hours = self.env['employee'].shift_hours_calc(
                rec.employee_shift_from, rec.employee_shift_to, rec.employee_shift_from_period, rec.employee_shift_to_period)

    @api.onchange('log_date')
    def is_weekend_checker(self):
        for rec in self:
            if rec.employee_id:
                day = calendar.weekday(
                    rec.log_date.year, rec.log_date.month, rec.log_date.day)
                if rec.employee_id.weekend[str(day)]:
                    rec.is_weekend = True
                else:
                    rec.is_weekend = False

    @api.onchange('employee_id')
    def default_shift_from_to(self):
        for rec in self:
            if rec.employee_id:
                rec.employee_shift_from = rec.employee_id.employee_shift_from
                rec.employee_shift_to = rec.employee_id.employee_shift_to
                rec.employee_shift_from_period = rec.employee_id.employee_shift_from_period
                rec.employee_shift_to_period = rec.employee_id.employee_shift_to_period
