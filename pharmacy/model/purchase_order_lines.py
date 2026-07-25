from odoo import models, fields, api


class PurchaseOrderLines(models.Model):
    _name = "purchase.order.lines"

    _rec_name = "purchase_id"

    purchase_id = fields.Many2one("purchase.order")
    barcode = fields.Integer(related="items_id.barcode", store=True, readonly=False)
    items_id = fields.Many2one("items", required=True)
    price = fields.Float(related="items_id.price", store=True, readonly=False)
    cost = fields.Float(related="items_id.cost", store=True, readonly=False)
    quantity = fields.Integer(required=True)
    exp_date = fields.Date(required=True)

    @api.onchange("barcode")
    def item_name_by_barcode(self):
        if self.barcode:
            item = self.env["items"].search([("barcode", "=", self.barcode)])
            if item:
                self.items_id = item.id
