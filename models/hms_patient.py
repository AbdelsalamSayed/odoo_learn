from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError


class HmsPatient(models.Model):
    _name = "hms.patient"
    _description = "Hms Patient"
    _rec_name = "full_name"
    first_name = fields.Char(string="First Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    full_name = fields.Char(string="Name", compute="_compute_name")
    birth_date = fields.Date(string="Birth Date")
    history = fields.Html()
    cr_ratio = fields.Float(string="CR Ratio")
    blood_type = fields.Selection(
        [
            ("o_p", "O+"),
            ("o_m", "O-"),
            ("a_p", "A+"),
            ("a_m", "A-"),
            ("b_p", "B+"),
            ("b_m", "B-"),
            ("ab_p", "AB+"),
            ("ab_m", "AB-"),
        ]
    )
    pcr = fields.Boolean(string="PCR")
    image = fields.Image()
    address = fields.Text()
    age = fields.Integer(compute="_compute_age")

    states = fields.Selection(
        [
            ("undetermined", "Undetermined"),
            ("good", "Good"),
            ("fair", "Fair"),
            ("serious", "Serious"),
        ],
        default="undetermined",
        string="Status",
    )
    department_id = fields.Many2one("hms.department")
    capacity = fields.Integer(related="department_id.capacity")
    doctors_ids = fields.Many2many("hms.doctors", string="Doctors")
    doctors_names = fields.Char(string="Doctor Name", compute="_compute_doctors_names")

    @api.depends("birth_date")
    def _compute_age(self):
        today = date.today()
        for rec in self:
            print(type(rec.birth_date))
            if rec.birth_date:
                age = (
                    today.year
                    - rec.birth_date.year
                    - (
                        (today.month, today.day)
                        < (rec.birth_date.month, rec.birth_date.day)
                    )
                )
                if age < 0:
                    raise ValidationError("wrong birth date")
                else:
                    rec.age = age
            else:
                rec.age = 0

    @api.depends("first_name", "last_name")
    def _compute_name(self):
        for rec in self:
            if rec.first_name and rec.last_name:
                rec.full_name = f"{rec.first_name} {rec.last_name}".strip()
            else:
                rec.full_name = ""

    @api.onchange("age")
    def _age_checker(self):
        for rec in self:
            if rec.age == 0:
                rec.pcr = False
            elif rec.age < 30:
                rec.pcr = True
                return {
                    "warning": {
                        "title": "warning",
                        "message": "PCR value changer automatic",
                        "type": "notification",
                    }
                }

    @api.constrains("pcr", "cr_ratio")
    def cr_ratio_checker(self):
        for rec in self:
            if rec.pcr and rec.cr_ratio == 0:
                raise ValidationError("please enter CR RAtio")
