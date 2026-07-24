from odoo import fields, models, api
from odoo.exceptions import ValidationError


class TasksDetails(models.Model):
    _name = 'tasks.details'

    day_date = fields.Date(required=True)
    description = fields.Text(required=True)
    taken_time = fields.Float(required=True, string='Taken Time /H')

    task_id = fields.Many2one('todo.task')

    @api.constrains('day_date')
    def day_date_checker(self):
        for rec in self:
            if rec.day_date > rec.task_id.due_date or rec.day_date < fields.Date.to_date(rec.create_date):
                raise ValidationError(
                    'Day date must be after creation date and before due date')
