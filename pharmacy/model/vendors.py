from odoo import fields, models, api


class Vendors(models.Model):
    _name = 'vendors'

    _rec_name = 'vendor_name'
    vendor_name = fields.Char()
    purchase_order_ids = fields.One2many('purchase.order', 'vendor_id')
    balance = fields.Float()

    def open_vendor_items_list(self):
        action = self.env['ir.actions.actions']._for_xml_id(
            'pharmacy.items_menu_action')
        action['domain'] = [("vendor_id", "=", self.id)]
        return action
