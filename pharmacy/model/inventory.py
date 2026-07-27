from odoo import models, fields, api


class Inventory(models.Model):
    _name = "inventory"

    item_id = fields.Many2one("items")
    unit_number = fields.Integer()
    quantity = fields.Integer()
    inventory = fields.Integer(compute="_compute_inventory")

    @api.depends("unit_number", "quantity")
    def _compute_inventory(self):
        for rec in self:
            rec.inventory = rec.quantity * rec.unit_number
