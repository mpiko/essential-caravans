from odoo import api, fields, models

class Production_Allocation(models.Model):
    _name = "dyman.production.allocation"
    _description = "Production allocation"
    _sql_constraints = [('unique_dealer_month', 'unique(dealer, build_month)', 'Slots have already been defined for this dealer and month')]

    dealer = fields.Many2one("dyman.dealer", string="Dealer", required=True, ondelete="cascade")
    build_month = fields.Many2one("dyman.build.month", string="Month", required=True, ondelete="cascade")
    slots = fields.Integer(string="Slots", required=True)