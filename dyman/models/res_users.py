from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    dyman_dealer_id = fields.Many2one("dyman.dealer", string="Dealership")
    