from odoo import models, fields, api


class EmployeeAttendance(models.Model):
    _name = 'employee.attendance'

    _rec_name = 'employee_id'
    employee_id = fields.Many2one('employee', readonly=True)
    related_user = fields.Many2one(
        'res.users', related='employee_id.related_user')
    employee_state = fields.Selection([], related='employee_id.state_in')
    in_time = fields.Datetime()
    out_time = fields.Datetime()
    hours = fields.Char(compute='_compute_time_calc')
    minutes = fields.Char(compute='_compute_time_calc')
    seconds = fields.Char(compute='_compute_time_calc')

    def check_in_to_employee(self):
        for rec in self:
            rec.employee_id.sudo().state_in = 'in'
            rec.in_time = fields.Datetime.now()

    def check_out_to_employee(self):
        for rec in self:
            rec.employee_id.sudo().state_in = 'out'
            rec.out_time = fields.Datetime.now()
            time = rec.out_time - rec.in_time
            total_seconds = int(time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600)//60
            self.env['employee.attendance.logs'].sudo().create({
                'employee_id': rec.employee_id.id,
                'in_time': rec.in_time,
                'out_time': rec.out_time,
            })
            rec.in_time = False
            rec.out_time = False

    @api.depends('employee_id', 'employee_state', 'in_time', 'hours', 'minutes', 'seconds')
    def _compute_time_calc(self):
        for rec in self:
            if rec.employee_state == 'in':
                time = fields.Datetime.now() - rec.in_time
                total_seconds = int(time.total_seconds())
                hours = total_seconds//3600
                minutes = total_seconds % 3600//60
                seconds = total_seconds % 60
                rec.hours = f'{hours:02d}'
                rec.minutes = f'{minutes:02d}'
                rec.seconds = f'{seconds:02d}'
                continue
            rec.hours = '00'
            rec.minutes = '00'
            rec.seconds = '00'
