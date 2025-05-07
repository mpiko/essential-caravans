from odoo import fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    dyman_order_id = fields.Many2one("dyman.order", string="Dynamic Manufacturing Order")
    