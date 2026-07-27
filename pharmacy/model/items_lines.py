from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ItemsLines(models.Model):
    _name = "items.lines"

    _rec_name = "receipt_number"

    receipt_number = fields.Char()
    purchase_id = fields.Many2one("purchase.order")
    adjustment_id = fields.Many2one('adjustment')
    barcode = fields.Integer(related="items_id.barcode",
                             store=True, readonly=False)
    items_id = fields.Many2one("items", required=True)
    vendor_id = fields.Many2one(
        related="items_id.vendor_id", store=True)
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

    @api.constrains('exp_date')
    def exp_date_check(self):
        for rec in self:
            if rec.exp_date < fields.Date.today():
                raise ValidationError("Please enter valid expire date")

    @api.constrains('quantity')
    def quantity_check(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError("Please enter valid quantity")
