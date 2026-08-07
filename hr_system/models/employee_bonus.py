from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EmployeeBonus(models.Model):
    _name = 'employee.bonus'
    _description = 'hr_system_employee_bonus'

    _rec_name = 'employee_id'
    employee_id = fields.Many2one('employee', default=lambda self: self.env['employee'].search(
        [('related_user', '=', self.env.user.id)]), limit=1, readonly=True)
    related_user = fields.Many2one(
        'res.users', related='employee_id.related_user', readonly=True)
    employee_role = fields.Selection([], related='employee_id.employee_role')
    bonus_day = fields.Date(
        required=True, default=fields.Date.today(), readonly=True)
    bonus_min = fields.Integer()
    bonus_state = fields.Selection([
        ('pending', 'pending'),
        ('wait_manager', 'Wait Manager'),
        ('wait_hr', 'Wait HR'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done')
    ],  default='pending', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(EmployeeBonus, self).create(vals_list)
        for rec in res:
            if len(self.env['employee.bonus'].search([('employee_id', '=', rec.employee_id.id), ('bonus_state', 'in', ['wait_manager', 'wait_hr', 'pending'])])) > 1:
                raise ValidationError(
                    "Your already have pending bonus")
        return res

    def employee_bonus_approve(self):
        for rec in self:
            rec.bonus_state = 'approved'

    def employee_bonus_reject(self):
        for rec in self:
            rec.bonus_state = 'rejected'

    def submit_my_bonus(self):
        for rec in self:
            if rec.employee_id.employee_role == "employee":
                rec.bonus_state = 'wait_manager'
            else:
                rec.bonus_state = 'wait_hr'

    def send_to_hr_bonus(self):
        for rec in self:
            rec.bonus_state = 'wait_hr'
