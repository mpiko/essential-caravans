from odoo import api, fields, models

class BaseMaterial(models.Model):
    _name = "dyman.base.material.update.log"
    _description = "Base product material update log"
    # A record of when a base material update has been applied.

    base_material_update_id = fields.Many2one("dyman.base.material.update", string="Base material update")
    applied_time = fields.Datetime(string="Applied")