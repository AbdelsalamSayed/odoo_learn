from odoo import models, fields, api
from odoo.exceptions import ValidationError
from enum import Enum


class Employee(models.Model):
    _name = "employee"
    _description = "employee_model_for_hr_system"

    _rec_name = "employee_name"
    user_account = fields.Many2one("res.users")
    employee_name = fields.Char(required=True)
    department_id = fields.Many2one(
        "departments", string="Department", required=True)
    employee_role = fields.Many2one("roles", required=True)
    employee_manager = fields.Many2one("employee")
    employee_number = fields.Char()
    employee_basic_salary = fields.Float(required=True)
    employee_birth_date = fields.Date()
    employee_image = fields.Image()
    employee_shift_from = fields.Float(default=8)
    employee_shift_to = fields.Float(default=4)
    active = fields.Boolean(default=True)
    employee_shift_hours = fields.Float(
        string="Total hours", compute="_compute_shift_hours"
    )
    employee_shift_from_period = fields.Selection(
        [
            ("am", "AM"),
            ("pm", "PM"),
        ],
        default="am",
        required=True,
    )
    employee_shift_to_period = fields.Selection(
        [
            ("am", "AM"),
            ("pm", "PM"),
        ],
        default="pm",
        required=True,
    )
    this_month = fields.Integer(
        default=fields.Date.today().month, readonly=True)
    end_sat = fields.Boolean()
    end_sun = fields.Boolean()
    end_mon = fields.Boolean()
    end_tus = fields.Boolean()
    end_wed = fields.Boolean()
    end_thu = fields.Boolean()
    end_fri = fields.Boolean()
    weekend = fields.Json(
        default=lambda self: {
            "5": False,
            "6": False,
            "0": False,
            "1": False,
            "2": False,
            "3": False,
            "4": False,
        },
        compute="week_end_list",
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(Employee, self).create(vals_list)
        for rec in res:
            if len(self.env['employee'].search([('user_account.id', '=', rec.user_account.id)])) > 1:
                raise ValidationError(
                    'This user account already has an employee account')
            if rec.employee_role.perm not in ["owner"] and not res.employee_manager:
                raise ValidationError("You must enter employee manager")
        return res

    def write(self, vals):
        res = super(Employee, self).write(vals)
        if 'user_account' in vals:
            for rec in self:
                if self.env['employee'].search_count([('user_account.id', '=', rec.user_account.id)]) > 1:
                    raise ValidationError(
                        "This user account is already linked to an employee")
        return res

    @api.depends(
        "employee_shift_from",
        "employee_shift_to",
        "employee_shift_from_period",
        "employee_shift_to_period",
    )
    def _compute_shift_hours(self):
        for rec in self:
            if not (rec.employee_shift_from or rec.employee_shift_to):
                rec.employee_shift_hours = 0
                continue
            if rec.employee_shift_from not in range(
                1, 13
            ) or rec.employee_shift_to not in range(1, 13):
                raise ValidationError("enter valid shift period")
            if rec.employee_shift_from_period == rec.employee_shift_to_period:
                if rec.employee_shift_from < rec.employee_shift_to:
                    rec.employee_shift_hours = (
                        rec.employee_shift_to - rec.employee_shift_from
                    )
                else:
                    rec.employee_shift_hours = (
                        12 - rec.employee_shift_from + 12 + rec.employee_shift_to
                    )
            else:
                rec.employee_shift_hours = (
                    12 - rec.employee_shift_from + rec.employee_shift_to
                )

    @api.depends(
        "end_sat", "end_sun", "end_mon", "end_tus", "end_wed", "end_thu", "end_fri"
    )
    def week_end_list(self):
        for rec in self:
            copy_weekend = dict(rec.weekend)
            copy_weekend["0"] = True if rec.end_mon else False
            copy_weekend["1"] = True if rec.end_tus else False
            copy_weekend["2"] = True if rec.end_wed else False
            copy_weekend["3"] = True if rec.end_thu else False
            copy_weekend["4"] = True if rec.end_fri else False
            copy_weekend["5"] = True if rec.end_sat else False
            copy_weekend["6"] = True if rec.end_sun else False
            rec.weekend = copy_weekend

    def open_attendance_logs(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_system.attendance_logs_action"
        )
        view_id = self.env.ref("hr_system.attendance_view_tree").id
        action["domain"] = [
            ("employee_id.user_account", "=", self.user_account.id)]
        action["views"] = [[view_id, "tree"]]
        return action

    def open_payroll_logs(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_system.payroll_menu_action"
        )
        action["domain"] = [
            ("employee_id.user_account", "=", self.user_account.id)]
        return action

    def open_loan_logs(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_system.employee_loan_action"
        )
        action["domain"] = [
            ("employee_id.user_account", "=", self.user_account.id)]

        return action

    def open_my_profile(self):
        my_profile = self.env['employee'].search(
            [('user_account', '=', self.env.user.id)]).id
        if not my_profile:
            raise ValidationError("No employee record is linked to your user account. "
                                  "Please contact HR.")
        action = self.env['ir.actions.actions']._for_xml_id(
            'hr_system.employee_model_view_action')
        view_id = self.env.ref('hr_system.employee_form_view').id
        action['res_id'] = my_profile
        action['views'] = [[view_id, 'form']]
        return action
