from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HmsDoctors(models.Model):
    _name = "hms.doctors"
    _description = "Hms Doctors"
    _rec_name = "full_name"
    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    full_name = fields.Char(string="Name", compute="_compute_name")
    image = fields.Image()
    department_id = fields.Many2one(
        "hms.department", string="Department", required=True
    )
    patient_ids = fields.Many2many("hms.patient", string="Patients", readonly=True)

    @api.depends("first_name", "last_name")
    def _compute_name(self):
        for rec in self:
            if rec.first_name and rec.last_name:
                rec.full_name = f"{rec.first_name} {rec.last_name}".strip()
            else:
                rec.full_name = ""

    def unlink(self):
        for rec in self:
            if len(rec.patient_ids) > 0:
                raise ValidationError(
                    "This doctor treats certain patients, so you cannot delete him"
                )

        return super().unlink()
