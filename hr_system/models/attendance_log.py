from odoo import models, fields, api
from odoo.exceptions import ValidationError
import calendar


class AttendanceLog(models.Model):
    _name = 'employee.attendance.logs'
    _description = 'hr_system_employee_attendance'

    _rec_name = 'employee_id'
    employee_id = fields.Many2one('employee', default=lambda self: self.env['employee'].search(
        [('related_user', '=', self.env.user.id)]), limit=1)
    log_time = fields.Datetime(default=fields.Datetime.now())
    is_weekend = fields.Boolean(default=False, readonly=True)
    log_type = fields.Selection([
        ('in', 'IN'),
        ('out', 'OUT')
    ])

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
