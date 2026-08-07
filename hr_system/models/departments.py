from odoo import models, fields, api


class Departments(models.Model):
    _name = 'departments'
    _description = 'hr_system_departments'

    _rec_name = 'department_name'
    department_name = fields.Char()
    department_capacity = fields.Integer(compute='get_department_capacity')
    department_lower_name = fields.Char(
        compute='_compute_department_lower_name', store=True)
    employee_ids = fields.One2many('employee', 'department_id', readonly=True)

    _sql_constraints = [
        ('unique_department_name', 'unique(department_lower_name)', 'this department already exists')]

    @api.depends('department_name')
    def _compute_department_lower_name(self):
        for rec in self:
            if rec.department_name:
                rec.department_lower_name = rec.department_name.lower()

    @api.depends('employee_ids', 'department_name')
    def get_department_capacity(self):
        for rec in self:
            rec.department_capacity = len(self.employee_ids)
