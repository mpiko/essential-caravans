from odoo import api, fields, models

class Component(models.Model):
    _name = "dyman.component"
    _description = "Dynamic product component"
    # Describes a component of a dynamic product, being a part of the product that will be fulfilled by a specific material

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')