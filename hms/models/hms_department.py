from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HmsDepartment(models.Model):
    _name = "hms.department"
    _description = "Hms Department"

    name = fields.Char(required=True)
    capacity = fields.Integer(compute="_compute_capacity")
    is_opened = fields.Boolean(string="Is Open", default=True)
    doctors_ids = fields.One2many(
        "hms.doctors", "department_id", string="Doctors", readonly=True
    )
    patient_ids = fields.One2many(
        "hms.patient", "department_id", readonly=True, string="Patients"
    )

    _sql_constraints = [('unique_name', 'unique("name")',
                         'This department already exists')]

    @api.depends("patient_ids.department_id")
    def _compute_capacity(self):
        for rec in self:
            rec.capacity = len(rec.patient_ids)

    def unlink(self):
        for rec in self:
            if len(rec.patient_ids) > 0:
                raise ValidationError(
                    f"{rec.name} department contains some patient; you cannot delete it"
                )
            elif len(rec.doctors_ids) > 0:
                raise ValidationError(
                    f"{rec.name} department contains some doctors; you cannot delete it"
                )
        return super().unlink()
