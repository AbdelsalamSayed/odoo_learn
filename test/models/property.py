from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Property(models.Model):
    _name = "property"

    ref = fields.Char(default="New", readonly=True)
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char(required=True)
    date_availability = fields.Date()
    expected_selling_date = fields.Date()
    is_late = fields.Boolean()
    selling_price = fields.Float()
    expected_price = fields.Float()
    diff = fields.Float(compute="_compute_diff")
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("sold", "Sold"),
            ("closed", "Closed"),
        ],
        default="draft",
    )
    garden_orientation = fields.Selection(
        [
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ]
    )
    owner_id = fields.Many2one("owner")
    owner_phone = fields.Char(related="owner_id.address")
    owner_address = fields.Char(related="owner_id.phone")
    tags_ids = fields.Many2many("tag")
    history = fields.One2many("property.history", "property_id")
    active = fields.Boolean(default=True)
    _sql_constraints = [
        ("unique_name", 'unique("name")', "invalid name"),
        ("unique_dis", 'unique("description")', "invalid dis"),
    ]

    def action(self):
        pass

    @api.depends("expected_price", "selling_price")
    def _compute_diff(self):
        for rec in self:
            rec.diff = rec.expected_price - rec.selling_price

    def action_draft(self):
        for rec in self:
            rec.create_property_history(rec.state, "draft")
            rec.state = "draft"

    def action_pending(self):
        for rec in self:
            rec.create_property_history(rec.state, "pending")
            rec.state = "pending"

    def action_sold(self):
        for rec in self:
            rec.create_property_history(rec.state, "sold")
            rec.state = "sold"

    def action_closed(self):
        for rec in self:
            rec.create_property_history(rec.state, "closed")
            rec.state = "closed"

    @api.constrains("bedrooms")
    def check_bedrooms(self):
        for record in self:
            if record.bedrooms <= 0:
                raise ValidationError("invalid bedroom number")

    def check_expected_selling_date(self):
        property_ids = self.search([])
        for rec in property_ids:
            if (
                rec.expected_selling_date
                and rec.expected_selling_date < fields.date.today()
            ):
                rec.is_late = True

    @api.model
    def create(self, vals):
        res = super(Property, self).create(vals)
        if res.ref == "New":
            res.ref = self.env["ir.sequence"].next_by_code("property_sequence")
        return res

    def create_property_history(self, old, new, reason="ـــ"):
        for rec in self:
            self.env["property.history"].create(
                {
                    "old_state": old,
                    "new_state": new,
                    "user_id": rec.env.uid,
                    "property_id": rec.id,
                    "reason": reason,
                }
            )

    def action_open_change_state_wizard(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "test.change_state_wizard_action"
        )
        action["context"] = {"default_property_id": self.id}
        return action

    def action_open_related_owner(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "test.owner_action")
        view_id = self.env.ref("test.owner_view_form").id
        action["res_id"] = self.owner_id.id
        action["views"] = [[view_id, "form"]]
        return action
