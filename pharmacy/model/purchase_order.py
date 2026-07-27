from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _name = "purchase.order"

    _rec_name = "purchase_number"
    purchase_number = fields.Char(default="PUR", readonly=True)

    cost = fields.Float()
    price = fields.Float()
    lines_ids = fields.One2many("items.lines", "purchase_id")
    vendor_id = fields.Many2one('vendors', required=True)

    @api.model
    def create(self, vals_list):
        res = super(PurchaseOrder, self).create(vals_list)
        res.purchase_number = self.env["ir.sequence"].next_by_code(
            "purchase_order_number_sequence_code"
        )
        inventory = self.env["inventory"]
        for rec in res.lines_ids:
            domain = [("item_id", "=", rec.items_id.id)]
            inventory.search(domain).quantity += rec.quantity
        for rec in res.lines_ids:
            rec.receipt_number = res.purchase_number
            res.vendor_id.balance += rec.cost*rec.quantity
        return res


# <field name="" context="{'form_view_ref':'pharmacy.items_purchase_order_form_view'}"/>
