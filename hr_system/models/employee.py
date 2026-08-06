from odoo import models, fields, api
from odoo.exceptions import ValidationError
import calendar

from datetime import datetime


class Employee(models.Model):
    _name = "employee"
    _description = "employee_model_for_hr_system"

    _rec_name = "employee_name"
    related_user = fields.Many2one("res.users")
    employee_name = fields.Char(
        related='related_user.name', readonly=False, store=True)
    employee_email = fields.Char(
        related='related_user.login', readonly=False, store=True)
    department_id = fields.Many2one(
        "departments", string="Department", readonly=False, store=True, related='related_user.department')
    employee_role = fields.Selection([
        ('owner', 'CEO / Owner'),
        ('hr', 'HR'),
        ('manager', 'Manager'),
        ('employee', 'employee'),
    ], related='related_user.role', readonly=False, store=True)
    employee_manager = fields.Many2one(
        related='related_user.manager', readonly=False, store=True)
    employee_number = fields.Char(
        related='related_user.mobile_number', readonly=False, store=True)
    employee_basic_salary = fields.Float(
        related='related_user.salary', readonly=False, store=True, required=True)
    employee_birth_date = fields.Date(
        related='related_user.birth_date', readonly=False, store=True)
    employee_image = fields.Binary(
        related='related_user.image_1920', readonly=False, store=True)
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
    state_in = fields.Selection([
        ('present', 'Present (by default)'),
        ('in', 'In'),
        ('out', 'Out'),
        ('yet_to_check_in', 'Yet To Check In'),
        ('weekend', 'Weekend'),
    ], default=lambda self: 'present' if self.employee_role == 'owner' else 'yet_to_check_in')

    def unlink(self):
        users_to_delete = self.env['res.users'].search(
            [('id', 'in', self.related_user.ids)])
        res = super(Employee, self).unlink()
        if users_to_delete:
            users_to_delete.unlink()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super(Employee, self).create(vals_list)
        for rec in res:
            if len(self.env['employee'].search([('related_user.id', '=', rec.related_user.id)])) > 1:
                raise ValidationError(
                    'This user account already has an employee account')
            if rec.employee_role not in ["owner"] and not rec.employee_manager:
                raise ValidationError("You must enter employee manager")
            self.env['employee.attendance'].create({
                'employee_id': rec.id
            })
        return res

    def write(self, vals):
        res = super(Employee, self).write(vals)
        if 'related_user' in vals:
            for rec in self:
                if self.env['employee'].search_count([('related_user.id', '=', rec.related_user.id)]) > 1:
                    raise ValidationError(
                        "This user account is already linked to an employee")
        return res

    @api.depends('employee_shift_from', 'employee_shift_to', 'employee_shift_from_period', 'employee_shift_to_period')
    def _compute_shift_hours(self):
        for rec in self:
            rec.employee_shift_hours = rec.shift_hours_calc(
                rec.employee_shift_from, rec.employee_shift_to, rec.employee_shift_from_period, rec.employee_shift_to_period)

    def shift_hours_calc(self, employee_shift_from, employee_shift_to, employee_shift_from_period, employee_shift_to_period):
        if not (employee_shift_from or employee_shift_to):
            employee_shift_hours = 0
            return employee_shift_hours
        if employee_shift_from not in range(
            1, 13
        ) or employee_shift_to not in range(1, 13):
            raise ValidationError("enter valid shift period")
        shift_from_24_system = employee_shift_from
        if employee_shift_from_period == 'pm' and employee_shift_from < 12:
            shift_from_24_system += 12
        elif employee_shift_from_period == 'am' and employee_shift_from == 12:
            shift_from_24_system = 0

        shift_to_24_system = employee_shift_to
        if employee_shift_to_period == 'pm' and employee_shift_to < 12:
            shift_to_24_system += 12
        elif employee_shift_to_period == 'am' and employee_shift_to == 12:
            shift_to_24_system = 0
        employee_shift_hours = shift_to_24_system-shift_from_24_system
        if employee_shift_hours < 0:
            return employee_shift_hours + 24
        return employee_shift_hours

    @api.depends('related_user')
    def related_user_details_compute(self):
        for rec in self:
            rec.employee_image = rec.related_user.image_1920
            rec.employee_email = rec.related_user.login
            rec.employee_name = rec.related_user.name

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
            ("employee_id.related_user", "=", self.related_user.id)]
        action["views"] = [[view_id, "tree"]]
        return action

    def open_payroll_logs(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_system.payroll_menu_action"
        )
        action["domain"] = [
            ("employee_id.related_user", "=", self.related_user.id)]
        return action

    def open_loan_logs(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "hr_system.employee_loan_action"
        )
        action["domain"] = [
            ("employee_id.related_user", "=", self.related_user.id)]
        return action

    def open_my_profile(self):
        my_profile = self.env['employee'].search(
            [('related_user', '=', self.env.user.id)]).id
        if not my_profile:
            raise ValidationError("No employee record is linked to your user account. "
                                  "Please contact HR.")
        action = self.env['ir.actions.actions']._for_xml_id(
            'hr_system.employee_model_view_action')
        view_id = self.env.ref('hr_system.employee_form_view').id
        action['res_id'] = my_profile
        action['views'] = [[view_id, 'form']]
        return action

    def open_my_attendance_profile(self):
        my_profile = self.env['employee.attendance'].search(
            [('related_user', '=', self.env.user.id)]).id
        if not my_profile:
            raise ValidationError("No attendance page linked to your user account. "
                                  "Please contact HR.")
        action = self.env['ir.actions.actions']._for_xml_id(
            'hr_system.attendance_action')
        view_id = self.env.ref('hr_system.employee_attendance_view_form').id
        action['res_id'] = my_profile
        action['views'] = [[view_id, 'form']]
        return action

    def check_employee_state(self):
        employees_ids = self.env['employee'].search([])
        for rec in employees_ids:
            if rec.state_in not in ['present', 'in']:
                roles_mapping = {
                    'owner': 'present',
                    'employee': 'yet_to_check_in',
                    'hr': 'yet_to_check_in',
                    'manager': 'yet_to_check_in',
                }
                week_end_days = next(
                    (k for k, v in rec.weekend.items() if v == True), False)
                if week_end_days:
                    today = datetime.now()
                    day_number = calendar.weekday(
                        today.year, today.month, today.day)
                    if str(day_number) in week_end_days:
                        rec.state_in = 'weekend'
                else:
                    rec.state_in = roles_mapping[rec.employee_role]
