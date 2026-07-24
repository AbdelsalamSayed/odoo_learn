from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_id = fields.Many2one('property')
    price = fields.Float(related='property_id.selling_price')
