from odoo import models, fields, api, Command
from datetime import date
from odoo.exceptions import ValidationError


class HmsPatient(models.Model):
    _name = "hms.patient"
    _description = "Hms Patient"
    _rec_name = "full_name"
    first_name = fields.Char(string="First Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    full_name = fields.Char(string="Name", compute="_compute_name")
    birth_date = fields.Date(string="Birth Date", required=True)
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
    logs_ids = fields.One2many("hms.patient.log", "patient_id")
    archived_state = fields.Selection(
        [("active", "Active"), ("archived", "Archived")], default="active"
    )

    @api.depends("birth_date")
    def _compute_age(self):
        today = date.today()
        for rec in self:
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

    def write(self, vals):
        log_create = []
        state_changed = False
        for rec in self:
            description = ""
            for key in vals:
                if key == "doctors_ids":
                    ids = rec.doctors_ids.ids
                    for command in vals[key]:
                        if isinstance(command, (list, tuple)):
                            cmd_type = command[0]
                            if cmd_type == 6:
                                ids = command[2]
                            elif cmd_type == 4:
                                if command[1] not in ids:
                                    ids.append(command[1])
                            elif cmd_type == 3:
                                if command[1] in ids:
                                    ids.remove(command[1])
                            elif cmd_type == 5:
                                ids = []
                    description += f"\t{key} changed from ({getattr(rec, key).mapped('full_name')}) to ({self.env['hms.doctors'].browse(ids).mapped('full_name')})"
                elif key == "department_id":
                    description += f"\t{key} changed from ({getattr(rec, key).mapped('name')}) to ({self.env['hms.department'].browse(vals[key]).mapped('name')})"
                elif key == "image":
                    description += "\tNew Image Uploded"
                elif key == "history":
                    description += "\tHistory changed"
                elif key == "logs_ids":
                    description += "\tMake edit in the logs"
                elif key == "archived_state" and vals[key] == "archived":
                    self.write(
                        {"doctors_ids": [Command.clear()], "department_id": False}
                    )
                    description += (
                        f"\t{key} changed from ({getattr(rec, key)}) to ({vals[key]})"
                    )
                else:
                    description += (
                        f"\t{key} changed from ({getattr(rec, key)}) to ({vals[key]})"
                    )

            replacement = {
                "first_name": "First Name",
                "last_name": "Last Name",
                "birth_date": "Birth Date",
                "department_id": "Department",
                "doctors_ids": "Doctors",
                "blood_type": "Blood Type",
                "cr_ratio": "CR Ratio",
                "pcr": "PCR",
            }
            for old, new in replacement.items():
                description = description.replace(old, new)
            log_create.append(
                {
                    "patient_id": rec.id,
                    "description": description,
                    "create_uid": self.env.user.id,
                    "create_date": fields.Datetime.now(),
                }
            )

        res = super(HmsPatient, self).write(vals)
        if log_create:
            self.env["hms.patient.log"].create(log_create)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            record = {
                "patient_id": rec.id,
                "description": "Patient created",
                "create_uid": rec.write_uid,
                "create_date": rec.write_date,
            }
            self.env["hms.patient.log"].create(record)
        return res

    def unlink(self):
        for rec in self:
            if len(rec.logs_ids) > 1:
                raise ValidationError(
                    "This patient has records, so you can't delete them, just archive them"
                )
                return
            else:
                res = super().unlink()
        return res

    @api.constrains("pcr", "cr_ratio")
    def cr_ratio_checker(self):
        for rec in self:
            if rec.pcr and rec.cr_ratio == 0:
                raise ValidationError("please enter CR RAtio")

    def state_good(self):
        for rec in self:
            rec.states = "good"

    def state_undetermined(self):
        for rec in self:
            rec.states = "undetermined"

    def state_fair(self):
        for rec in self:
            rec.states = "fair"

    def state_serious(self):
        for rec in self:
            rec.states = "serious"


class HmsPatientLog(models.Model):
    _name = "hms.patient.log"
    _description = "Patient Log"

    patient_id = fields.Many2one("hms.patient")
    description = fields.Text()
