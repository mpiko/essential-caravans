from odoo import api, fields, models

class AttribueValue(models.Model):
    _name = "dyman.attribute.value"
    _description = "Dynamic attribute value"
    # Describes a value, which when matched with an attribute type can be used to define a dynamic product

    name = fields.Char(string='Name', required=True)