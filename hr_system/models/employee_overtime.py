from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EmployeeOvertime(models.Model):
    _name = 'employee.overtime'
    _description = 'hr_system_employee_overtime'

    _rec_name = 'employee_id'
    employee_id = fields.Many2one('employee', default=lambda self: self.env['employee'].search(
        [('related_user', '=', self.env.user.id)]), limit=1, readonly=True)
    related_user = fields.Many2one(
        'res.users', related='employee_id.related_user', readonly=True)
    employee_role = fields.Selection([], related='employee_id.employee_role')
    overtime_day = fields.Date(
        required=True, default=fields.Date.today(), readonly=True)
    overtime_min = fields.Integer()
    overtime_state = fields.Selection([
        ('pending', 'pending'),
        ('wait_manager', 'Wait Manager'),
        ('wait_hr', 'Wait HR'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done')
    ],  default='pending', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(EmployeeOvertime, self).create(vals_list)
        for rec in res:
            if len(self.env['employee.overtime'].search([('employee_id', '=', rec.employee_id.id), ('overtime_state', 'in', ['wait_manager', 'wait_hr', 'pending'])])) > 1:
                raise ValidationError(
                    "Your already have pending overtime")
        return res

    def employee_overtime_approve(self):
        for rec in self:
            rec.overtime_state = 'approved'

    def employee_overtime_reject(self):
        for rec in self:
            rec.overtime_state = 'rejected'

    def submit_my_overtime(self):
        for rec in self:
            if rec.employee_id.employee_role == "employee":
                rec.overtime_state = 'wait_manager'
            else:
                rec.overtime_state = 'wait_hr'

    def send_to_hr_overtime(self):
        for rec in self:
            rec.overtime_state = 'wait_hr'
