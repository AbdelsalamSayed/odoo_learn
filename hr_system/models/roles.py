from odoo import models, fields, api


class Roles(models.Model):
    _name = 'roles'
    _description = 'hr_system_roles'

    _rec_name = 'role_name'
    role_name = fields.Char(required=True)
    lower_name = fields.Char(compute='_compute_lower_name', store=True)

    _sql_constraints = [
        ('unique_role_name', 'unique(lower_name)', "this role already exists")]

    @api.depends('role_name')
    def _compute_lower_name(self):
        for rec in self:
            if rec.role_name:
                rec.lower_name = rec.role_name.lower()
