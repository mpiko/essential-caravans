from odoo import api, fields, models

class BuildYear(models.Model):
    _name = "dyman.build.year"
    _description = "Build year"

    name = fields.Integer(string='Name', required=True)