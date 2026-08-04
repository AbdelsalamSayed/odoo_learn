from odoo import models, fields, api


class EmployeeAttendance(models.TransientModel):
    _name = 'employee.attendance'

    _rec_name = 'employee_id'
    employee_id = fields.Many2one('employee', default=lambda self: self.env['employee'].search(
        [('related_user', '=', self.env.user.id)]), limit=1, readonly=True)
    employee_state = fields.Selection([], related='employee_id.state_in')
    hours = fields.Integer(
        default=lambda self: self._default_hours_calc(), readonly=True)
    minutes = fields.Integer(
        default=lambda self: self._default_minutes_calc(), readonly=True)
    seconds = fields.Integer(
        default=lambda self: self._default_seconds_calc(), readonly=True)

    def check_in_to_employee(self):
        for rec in self:
            rec.employee_id.sudo().state_in = 'in'
            self.env['employee.attendance.logs'].sudo().create({
                'employee_id': rec.employee_id.id,
                'log_time': fields.Datetime.now(),
                'log_type': 'in'
            })

    def check_out_to_employee(self):
        for rec in self:
            rec.employee_id.sudo().state_in = 'out'
            self.env['employee.attendance.logs'].sudo().create({
                'employee_id': rec.employee_id.id,
                'log_time': fields.Datetime.now(),
                'log_type': 'out'
            })

    def _default_hours_calc(self):
        print(self.employee_id.id)
        print(self)
        print('vhdjndbdjnvdjbjkdzb')
        last_in = self.env['employee.attendance.logs'].search([
            ('log_type', '=', 'in'), ('employee_id', '=', self.employee_id.id)
        ], order='id desc', limit=1)
        hours = 0
        if last_in:
            print(last_in)
            now = fields.Datetime.now()-last_in.log_time
            total_seconds = int(now.total_seconds())
            hours = total_seconds // 3600
        return hours

    def _default_minutes_calc(self):
        last_in = self.env['employee.attendance.logs'].search([
            ('log_type', '=', 'in'), ('employee_id', '=', self.employee_id.id)
        ], order='id desc', limit=1)
        minutes = 0
        if last_in:
            print(last_in)
            now = fields.Datetime.now()-last_in.log_time
            total_seconds = int(now.total_seconds())
            minutes = (total_seconds % 3600)//60
        return minutes

    def _default_seconds_calc(self):
        last_in = self.env['employee.attendance.logs'].search([
            ('log_type', '=', 'in'), ('employee_id', '=', self.employee_id.id)
        ], order='id desc', limit=1)
        seconds = 0
        if last_in:
            print(last_in)
            now = fields.Datetime.now()-last_in.log_time
            total_seconds = int(now.total_seconds())
            seconds = total_seconds % 60
        return seconds
