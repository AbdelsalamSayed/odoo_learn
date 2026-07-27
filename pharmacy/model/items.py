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
    inventory = fields.One2many('inventory', 'item_id')
    inventory_quantity_pack = fields.Integer(
        related='inventory.quantity', string='Quantity/Pack')
    inventory_quantity_unit = fields.Integer(
        related='inventory.inventory', string='Quantity/unit')
    vendor_id = fields.Many2one('vendors')

    _sql_constraints = [("unique_name", "unique(name)",
                         "this item already exists")]

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
        res.barcode = self.env["ir.sequence"].next_by_code(
            "barcode_sequence_code")
        self.env["inventory"].create(
            {"item_id": res.id, "unit_number": res.number_of_units, "quantity": "0"}
        )
        return res

    def action_open_history(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "pharmacy.history_action")
        view_id = self.env.ref(
            "pharmacy.items_lines_history_tree_view").id
        action["domain"] = [("items_id", "=", self.id)]
        action["views"] = [[view_id, "tree"]]
        return action
