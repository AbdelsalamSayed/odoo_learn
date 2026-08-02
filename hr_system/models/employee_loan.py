from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EmployeeLoan(models.Model):
    _name = 'employee.loan'
    _description = 'hr_system_employee_loan'

    _rec_name = 'employee_id'
    employee_id = fields.Many2one('employee', default=lambda self: self.env['employee'].search(
        [('related_user', '=', self.env.user.id)]), limit=1)
    related_user = fields.Many2one(
        'res.users', related='employee_id.related_user')
    start_loan_month = fields.Date(
        required=True, string='First payment at', default=fields.Date.today())
    loan_amount = fields.Float(required=True)
    loan_repayment_period = fields.Integer(default=1)
    remaining_amount = fields.Float(readonly=True)
    loan_state = fields.Selection([
        ('pending', 'pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ],  default='pending')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(EmployeeLoan, self).create(vals_list)
        for rec in res:
            if rec.loan_amount <= 0:
                raise ValidationError(
                    "Please enter valid amounts in ('Loan Amount')")
            if rec.loan_amount*100/rec.employee_id.employee_basic_salary > 40:
                raise ValidationError(
                    "Your loan limit is 40% of your basic salary")
            if self.env['employee.loan'].search([('employee_id', '=', rec.employee_id.id), ('loan_state', 'in', ['approved', 'pending'])]):
                raise ValidationError(
                    "Your already have unpaid loan")
            rec.remaining_amount = rec.loan_amount
        return res

    def employee_loan_approve(self):
        for rec in self:
            rec.loan_state = 'approved'

    def employee_loan_reject(self):
        for rec in self:
            rec.loan_state = 'rejected'
