from odoo import api, fields, models

class Operation(models.Model):
    _name = "dyman.operation"
    _description = "Dynamic manufacturing operation"
    # Describes an operation in the process of producing a dynamic product

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')