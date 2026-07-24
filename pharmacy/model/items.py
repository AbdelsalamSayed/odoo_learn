from odoo import models, fields, api


class Items(models.Model):
    _name = "items"

    barcode = fields.Integer(readonly=True)
    name = fields.Char(required=True)
    description = fields.Text()
    cost = fields.Float()
    price = fields.Float(required=True)
    profit = fields.Float(compute="_compute_profit_calc")
    unit_of_measure = fields.Selection(
        [("pack", "Pack"), ("unit", "Unit")], default="pack"
    )
    number_of_units = fields.Integer(default=1)

    @api.depends("price", "cost")
    def _compute_profit_calc(self):
        for rec in self:
            if rec.price and rec.cost:
                rec.profit = (rec.price - rec.cost) * 100 / rec.cost
            else:
                rec.profit = 0

    @api.model
    def create(self, vals):
        res = super(Items, self).create(vals)
        res.barcode = self.env["ir.sequence"].next_by_code("barcode_sequence_code")
        self.env["inventory"].create(
            {"item_id": res.id, "unit_number": res.number_of_units, "quantity": "0"}
        )
        return res
