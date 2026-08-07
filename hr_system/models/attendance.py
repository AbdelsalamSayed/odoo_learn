from odoo import models, fields, api
from odoo.exceptions import ValidationError


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
            rec.sudo().in_time = fields.Datetime.now()

    def check_out_to_employee(self):
        for rec in self:
            rec.employee_id.sudo().state_in = 'out'
            rec.sudo().out_time = fields.Datetime.now()
            self.env['employee.attendance.logs'].sudo().create({
                'employee_id': rec.employee_id.id,
                'in_time': rec.in_time,
                'out_time': rec.out_time,
            })
            rec.sudo().in_time = False
            rec.sudo().out_time = False

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

    def open_my_attendance(self):
        my_account = self.env['employee'].search(
            [('related_user', '=', self.env.user.id)])
        my_profile = self.env['employee.attendance'].search(
            [('related_user', '=', self.env.user.id)]).id
        if my_account.employee_role == 'owner':
            action = self.env['ir.actions.actions']._for_xml_id(
                'hr_system.employee_model_view_action')
        else:
            action = self.env['ir.actions.actions']._for_xml_id(
                'hr_system.attendance_action')
            view_id = self.env.ref(
                'hr_system.employee_attendance_view_form').id
            action['views'] = [[view_id, 'form']]
            if not my_profile:
                new_profile = self.env['employee.attendance'].create({
                    'employee_id': my_account.id
                })
                action['res_id'] = new_profile
            else:
                action['res_id'] = my_profile
        return action

    def open_attendance_logs(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_system.attendance_logs_action"
        )
        view_id = self.env.ref("hr_system.attendance_view_tree").id
        action["domain"] = [
            ("employee_id.related_user", "=", self.related_user.id)]
        action["views"] = [[view_id, "tree"]]
        return action

    def open_payroll_logs(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_system.payroll_menu_action"
        )
        action["domain"] = [
            ("employee_id.related_user", "=", self.related_user.id)]
        return action

    def open_loan_logs(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_system.employee_loan_action"
        )
        action["domain"] = [
            ("employee_id.related_user", "=", self.related_user.id)]
        return action

    def open_bonus_logs(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_system.employee_bonus_action"
        )
        action["domain"] = [
            ("employee_id.related_user", "=", self.related_user.id)]
        return action

    def open_overtime_logs(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_system.employee_overtime_action"
        )
        action["domain"] = [
            ("employee_id.related_user", "=", self.related_user.id)]
        return action

    def open_my_profile(self):
        my_profile = self.env['employee'].search(
            [('related_user', '=', self.env.user.id)]).id
        if not my_profile:
            raise ValidationError("No employee record is linked to your user account. "
                                  "Please contact HR.")
        action = self.env['ir.actions.actions']._for_xml_id(
            'hr_system.employee_model_view_action')
        view_id = self.env.ref('hr_system.employee_form_view').id
        action['res_id'] = my_profile
        action['views'] = [[view_id, 'form']]
        return action
