from odoo import fields, models, api


class Adjustment(models.Model):
    _name = 'adjustment'

    _rec_name = 'adjustment_number'
    adjustment_number = fields.Char(default='ADJ', readonly=True)
    adjustment_type = fields.Selection([
        ('positive', 'Positive'),
        ('negative', 'Negative')
    ], default='positive')
    lines_ids = fields.One2many("items.lines", "adjustment_id")

    @api.model
    def create(self, vals_list):
        res = super(Adjustment, self).create(vals_list)
        if res.adjustment_type == 'positive':
            res.adjustment_number = self.env['ir.sequence'].next_by_code(
                'positive_adjustment_number_sequence_code')
            inventory = self.env["inventory"]
            for rec in res.lines_ids:
                domain = [("item_id", "=", rec.items_id.id)]
                inventory.search(domain).quantity += rec.quantity
        elif res.adjustment_type == 'negative':
            res.adjustment_number = self.env['ir.sequence'].next_by_code(
                'negative_adjustment_number_sequence_code')
            inventory = self.env["inventory"]
            for rec in res.lines_ids:
                domain = [("item_id", "=", rec.items_id.id)]
                inventory.search(domain).quantity -= rec.quantity
        for rec in res.lines_ids:
            rec.receipt_number = res.adjustment_number
        return res
