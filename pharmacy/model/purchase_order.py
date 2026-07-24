from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _name = 'purchase_order'

    purchase_number = fields.Char(default='PUR')
    items_ids = fields.One2many('items', 'purchase_order_id')
    cost = fields.Float()
    price = fields.Float()
    amount = fields.Integer()


# <field name="" context="{'form_view_ref':'pharmacy.items_purchase_order_form_view'}"/>
