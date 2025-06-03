from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    dyman_dealer_user_access_ids = fields.One2many("dyman.dealer.user.access", "user_id", string="Dealership permissions")
    