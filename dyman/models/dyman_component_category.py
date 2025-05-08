from odoo import api, fields, models

class ComponentCategory(models.Model):
    _name = "dyman.component.category"
    _description = "Dynamic product component category"
    # Describes a category under which components of a dynamic product will be grouped

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')