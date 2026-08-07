from odoo import models, fields, api
import calendar
import pytz
from datetime import timedelta
from odoo.exceptions import ValidationError


class AttendanceLog(models.Model):
    _name = 'employee.attendance.logs'
    _description = 'hr_system_employee_attendance'

    _rec_name = 'employee_id'
    employee_id = fields.Many2one('employee', default=lambda self: self.env['employee'].search(
        [('related_user', '=', self.env.user.id)], limit=1))
    in_time = fields.Datetime()
    out_time = fields.Datetime()
    start_shift = fields.Datetime(
        default=lambda self: self.default_start_shift(), store=True, readonly=False)
    end_shift = fields.Datetime(
        default=lambda self: self.default_end_shift(), store=True, readonly=False)
    is_weekend = fields.Boolean(
        default=False, compute='is_weekend_checker', string='Weekend')
    is_late = fields.Boolean(
        default=False, compute='is_late_checker', string='Late')
    worked_hours = fields.Float(compute='_compute_worked_hours')
    salary_hours = fields.Float(compute='_compute_salary_hours')

    @api.constrains('end_shift', 'start_shift', 'in_time', 'out_time')
    def _check_shift_and_attendance(self):
        for rec in self:
            if not (rec.in_time and rec.out_time):
                raise ValidationError("you must enter in-time and out-ime")
            if rec.out_time < rec.in_time:
                raise ValidationError("Out-time must be after in-time")
            if rec.end_shift <= rec.start_shift:
                raise ValidationError("end_shift must be after start_shift")

    @api.model
    def default_start_shift(self):
        rec = self.env['employee'].search(
            [('related_user', '=', self.env.user.id)], limit=1)
        start_shift = False
        if rec:
            local_in_time = fields.Datetime.context_timestamp(
                self, fields.Datetime.now())
            shift_start_at = int(rec.employee_shift_from)
            shift_start_at_period = rec.employee_shift_from_period
            if shift_start_at_period == 'am' and shift_start_at == 12:
                shift_start_at = 0
            elif shift_start_at_period == 'pm':
                shift_start_at += 12
            start_target = local_in_time.replace(
                hour=shift_start_at, minute=0, second=0, microsecond=0)
            start_shift = start_target.astimezone(
                pytz.utc).replace(tzinfo=None)
            return start_shift

    @api.model
    def default_end_shift(self):
        rec = self.env['employee'].search(
            [('related_user', '=', self.env.user.id)], limit=1)
        end_shift = False
        if rec:
            local_in_time = fields.Datetime.context_timestamp(
                self, fields.Datetime.now())
            shift_end_at = int(rec.employee_shift_to)
            shift_end_at_period = rec.employee_shift_to_period
            if shift_end_at_period == 'am' and shift_end_at == 12:
                shift_end_at = 0
            elif shift_end_at_period == 'pm':
                shift_end_at += 12
            end_target = local_in_time.replace(
                hour=shift_end_at, minute=0, second=0, microsecond=0)
            end_shift = end_target.astimezone(
                pytz.utc).replace(tzinfo=None)
            if end_shift < self.default_start_shift():
                end_shift += timedelta(days=1)
            return end_shift

    @api.depends('employee_id', 'in_time', 'out_time', 'start_shift', 'end_shift')
    def is_weekend_checker(self):
        for rec in self:
            if rec.employee_id and rec.start_shift:
                day = calendar.weekday(
                    rec.start_shift.year, rec.start_shift.month, rec.start_shift.day)
                if rec.employee_id.weekend[str(day)]:
                    rec.is_weekend = True
                    continue
            rec.is_weekend = False

    @api.depends('employee_id', 'in_time', 'out_time', 'start_shift', 'end_shift')
    def is_late_checker(self):
        for rec in self:
            if rec.employee_id and rec.in_time and rec.start_shift:
                time = rec.in_time - rec.start_shift
                total_hours = time.total_seconds() / 3600
                if total_hours > 0.25:
                    rec.is_late = True
                    continue
            rec.is_late = False

    @api.depends('worked_hours')
    def _compute_salary_hours(self):
        for rec in self:
            salary = 0
            if rec.worked_hours > 0 and rec.start_shift:
                time = (rec.in_time - rec.start_shift).total_seconds()
                late_time = time/3600
                real_worked_hours = int(
                    rec.worked_hours) + (((rec.worked_hours-int(rec.worked_hours))*100)/60)
                if rec.is_late:
                    salary = real_worked_hours - (late_time*0.5)
                else:
                    salary = real_worked_hours if real_worked_hours <= rec.employee_id.employee_shift_hours else rec.employee_id.employee_shift_hours
            rec.salary_hours = int(salary) + \
                (((salary - int(salary))*60)/100)

    @api.depends('in_time', 'out_time', 'start_shift', 'end_shift')
    def _compute_worked_hours(self):
        for rec in self:
            if rec.in_time and rec.out_time:
                time = rec.out_time - rec.in_time
                hours = time.total_seconds() // 3600
                minutes = time.total_seconds() % 3600 // 60
                rec.worked_hours = hours+(minutes/100)
                continue
            rec.worked_hours = 0

    def default_shift_shift(self):
        for rec in self:
            end_shift = False
            start_shift = False
            if rec:
                local_in_time = fields.Datetime.context_timestamp(
                    self, fields.Datetime.now())
                shift_start_at = int(rec.employee_id.employee_shift_from)
                shift_start_at_period = rec.employee_id.employee_shift_from_period
                if shift_start_at_period == 'am' and shift_start_at == 12:
                    shift_start_at = 0
                elif shift_start_at_period == 'pm':
                    shift_start_at += 12
                start_target = local_in_time.replace(
                    hour=shift_start_at, minute=0, second=0, microsecond=0)
                start_shift = start_target.astimezone(
                    pytz.utc).replace(tzinfo=None)
                shift_end_at = int(rec.employee_id.employee_shift_to)
                shift_end_at_period = rec.employee_id.employee_shift_to_period
                if shift_end_at_period == 'am' and shift_end_at == 12:
                    shift_end_at = 0
                elif shift_end_at_period == 'pm':
                    shift_end_at += 12
                end_target = local_in_time.replace(
                    hour=shift_end_at, minute=0, second=0, microsecond=0)
                end_shift = end_target.astimezone(
                    pytz.utc).replace(tzinfo=None)
                if end_shift < start_shift:
                    end_shift += timedelta(days=1)
                this_rec = self.env['employee.attendance.logs'].search(
                    [('id', '=', rec.id)])
                this_rec.write({
                    'start_shift': start_shift,
                    'end_shift': end_shift
                })
