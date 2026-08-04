from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Users(models.Model):
    _inherit = 'res.users'

    department = fields.Many2one('departments', required=True)
    role = fields.Selection([
        ('owner', 'Owner'),
        ('hr', 'HR'),
        ('manager', 'Manager'),
        ('employee', 'employee'),
    ], required=True, default='employee')
    manager = fields.Many2one('employee', domain=[(
        'employee_role', 'in', ['owner', 'manager'])])
    salary = fields.Float()
    birth_date = fields.Date()
    mobile_number = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            if (rec.salary < 0):
                raise ValidationError('salary must be greater than 0')
            rec.write({
                'password': '1234',
                'groups_id': self.get_group_id(rec.role)
            })
            self.env['employee'].create({
                'employee_name': rec.name,
                'related_user': rec.id,
                'employee_email': rec.login,
                'department_id': rec.department.id,
                'employee_role': rec.role,
                'employee_manager': rec.manager.id,
                'employee_basic_salary': rec.salary or 0,
                'employee_image': rec.image_1920,
                'employee_number': rec.mobile_number,
                'employee_birth_date': rec.birth_date
            })
        return res

    def create_employee_button_action(self):
        for rec in self:
            if (rec.salary < 0):
                raise ValidationError('salary must be greater than 0')
            rec.write({
                'groups_id': self.get_group_id(rec.role)
            })
            self.env['employee'].create({
                'employee_name': rec.name,
                'related_user': rec.id,
                'employee_email': rec.login,
                'department_id': rec.department.id,
                'employee_role': rec.role,
                'employee_manager': rec.manager.id,
                'employee_basic_salary': rec.salary or 0,
                'employee_image': rec.image_1920,
                'employee_number': rec.mobile_number,
                'employee_birth_date': rec.birth_date
            })

    def unlink(self):
        employees_to_delete = self.env['employee'].search(
            [('related_user', 'in', self.ids)])
        res = super(Users, self).unlink()
        if employees_to_delete:
            employees_to_delete.unlink()
        return res

    @api.model
    def write(self, vals):
        if 'role' in vals:
            for rec in self:
                new_role = vals.get('role')
                rec.write({
                    'groups_id': self.get_group_id(new_role)
                })
        res = super().write(vals)
        return res

    @api.model
    def get_group_id(self, new_role):
        role_mapping = {
            'owner': ['hr_system.ceo_groups_record', 'base.group_system', 'base.group_partner_manager'],
            'hr': ['hr_system.hr_perm_group', 'base.group_partner_manager'],
            'manager': ['hr_system.manager_perm_group'],
            'employee': ['hr_system.employee_perm_group']
        }
        group_ids_to_add = []
        if new_role in role_mapping:
            for rec in role_mapping[new_role]:
                group = self.env.ref(rec)
                if group:
                    group_ids_to_add.append(group.id)
        command = []
        for g_id in group_ids_to_add:
            command.append(g_id)
        command.append(self.env.ref('base.group_user').id)
        return [(6, 0, command)]
