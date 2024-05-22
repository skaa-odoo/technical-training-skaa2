from odoo import fields, models

class estate_property_tag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tags"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Name should be unique.')]
