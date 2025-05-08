from odoo import api, fields, models

class AttribueType(models.Model):
    _name = "dyman.attribute.type"
    _description = "Dynamic attribute type"
    # Describes a type of attribute that can be used to define a dynamic product

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')