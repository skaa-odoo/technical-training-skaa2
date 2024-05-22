from odoo import fields, models, api

class estate_property_type(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Types"
    _order = "name"

    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id")
    sequence = fields.Integer()
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")
    offer_count = fields.Integer(compute="_compute_offer_count")

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for it in self:
            it.offer_count=len(it.offer_ids)

    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Name should be unique.')]