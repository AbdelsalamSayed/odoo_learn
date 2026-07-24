from odoo import models, fields, api


class Items(models.Model):
    _name = 'items'

    barcode = fields.Integer(readonly=True)
    name = fields.Char(required=True)
    description = fields.Text()
    cost = fields.Float()
    price = fields.Float(required=True)
    profit = fields.Float(compute='_compute_profit_calc')
    unit_of_measure = fields.Selection([
        ('pack', 'Pack'),
        ('unit', 'Unit')
    ])
    number_of_units = fields.Integer(
        default=1)
    exp_date = fields.Date(required=True)
    amount = fields.Integer(required=True)
    inventory = fields.Integer(compute='_compute_inventory_calc')
    purchase_order_id = fields.Many2one('purchase_order')

    @api.depends('amount', 'number_of_units')
    def _compute_inventory_calc(self):
        for rec in self:
            if rec.amount and rec.number_of_units:
                rec.inventory = rec.amount * rec.number_of_units
            else:
                rec.inventory = 0

    @api.depends('price', 'cost')
    def _compute_profit_calc(self):
        for rec in self:
            if rec.price and rec.cost:
                rec.profit = (rec.price - rec.cost)*100/rec.cost
            else:
                rec.inventory = 0

    @api.model
    def create(self, vals):
        res = super(Items, self).create(vals)
        res.barcode = self.env['ir.sequence'].next_by_code(
            'barcode_sequence_code')
        return res
