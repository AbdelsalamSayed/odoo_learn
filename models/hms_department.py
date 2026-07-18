from odoo import models, fields, api


class HmsDepartment(models.Model):
    _name = "hms.department"
    _description = "Hms Department"

    name = fields.Char()
    capacity = fields.Integer(compute="_compute_capacity")
    is_opened = fields.Boolean(string="Is Open")
    doctors_ids = fields.One2many(
        "hms.doctors", "department_id", string="Doctors", readonly=True
    )
    patient_ids = fields.One2many(
        "hms.patient", "department_id", readonly=True, string="Patients"
    )

    @api.depends("patient_ids.department_id")
    def _compute_capacity(self):
        for rec in self:
            rec.capacity = len(rec.patient_ids)
