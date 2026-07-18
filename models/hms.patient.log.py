from odoo import models, fields, api


class HmsPatientLog(models.Model):
    _name = "hms.patient.log"
    _description = "Patient Log"

    description = fields.Char()
