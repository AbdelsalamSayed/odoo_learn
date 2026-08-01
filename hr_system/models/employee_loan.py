from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EmployeeLoan(models.Model):
    _name = 'employee.loan'
    _description = 'hr_system_employee_loan'

    _rec_name = 'employee_id'
    employee_id = fields.Many2one('employee', default=lambda self: self.env['employee'].search(
        [('user_account', '=', self.env.user.id)]), limit=1)
    user_account = fields.Many2one(
        'res.users', related='employee_id.user_account')
    start_loan_month = fields.Date(required=True)
    loan_amount = fields.Float(required=True)
    loan_repayment_period = fields.Integer(required=True)
    loan_paid = fields.Float(required=True)
    loan_state = fields.Selection([
        ('', ''),
        ('pending', 'pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ],  default='pending')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(EmployeeLoan, self).create(vals_list)
        for rec in res:
            if rec.loan_amount <= 0 or rec.loan_repayment_period <= 0:
                raise ValidationError(
                    "Please enter valid amounts in ('Loan Amount'),('Loan Repayment Period')")
        return res

    def employee_loan_approve(self):
        for rec in self:
            rec.loan_state = 'approved'

    def employee_loan_reject(self):
        for rec in self:
            rec.loan_state = 'rejected'
