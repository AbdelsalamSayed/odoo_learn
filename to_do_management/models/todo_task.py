from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ToDoTask(models.Model):
    _name = 'todo.task'

    task_name = fields.Char(required=True)
    assign_to = fields.Many2one('res.partner', required=True)
    description = fields.Text(required=True)
    due_date = fields.Date(required=True)
    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed')
    ], default='new')
    active = fields.Boolean(default=True)
    estimated_time = fields.Float(required=True)
    details_ids = fields.One2many('tasks.details', 'task_id')
    is_late = fields.Boolean()

    @api.constrains('details_ids')
    def total_taken_time_calc(self):
        for rec in self:
            total_taken_time = 0
            for time in rec.details_ids:
                if time.taken_time == 0:
                    raise ValidationError(
                        "Taken time must be grater than 0")
                else:
                    total_taken_time += time.taken_time
            if total_taken_time > rec.estimated_time:
                raise ValidationError(
                    "Total taken time must be equal or less than estimated time")

    def state_new(self):
        for rec in self:
            rec.status = 'new'

    def state_in_progress(self):
        for rec in self:
            rec.status = 'in_progress'

    def state_completed(self):
        for rec in self:
            rec.status = 'completed'

    def state_closed(self):
        for rec in self:
            rec.status = 'closed'

    @api.constrains('due_date')
    def date_checker(self):
        for rec in self:
            if rec.due_date < fields.Date.today():
                raise ValidationError("you can't choose date before today")

    def check_due_date(self):
        task_ids = self.search(
            [('status', '!=', 'completed'), ('active', '=', True), ('status', '!=', 'closed')])
        for rec in task_ids:
            if rec.due_date and rec.due_date < fields.Date.today():
                rec.is_late = True
                rec.status = 'closed'
