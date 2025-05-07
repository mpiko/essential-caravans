from odoo import api, fields, models

class BaseMaterial(models.Model):
    _name = "dyman.base.characteristic.update.log"
    _description = "Base product characteristic update log"
    # A record of when a base product characteristic has been applied.

    base_characteristic_update_id = fields.Many2one("dyman.base.characteristic.update", string="Base characteristic update")
    applied_time = fields.Datetime(string="Applied")