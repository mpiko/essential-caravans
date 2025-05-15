from odoo import api, fields, models

class DealerUserAccess(models.Model):
    _name = "dyman.dealer.user.access"
    _description = "Dealership user access"
    # User access to dealership data for portal users

    dealer_id = fields.Many2one("dyman.dealer", string="Dealership", required=True, ondelete="cascade")
    user_id = fields.Many2one("res.users", string="User", required=True, ondelete="restrict")
    can_submit = fields.Boolean(string="Can submit?")
    can_sign = fields.Boolean(string="Can sign")