from odoo import api, fields, models

class ProductLineDealerRestriction(models.Model):
    _name = "dyman.prodline.dealer.restriction"
    _description = "Dynamic product line dealer restriction"
    # A product line can be restricted to specific dealers.

    name = fields.Char(string='Name', related="dealer_id.name")
    product_line_id = fields.Many2one("dyman.product.line", string="Product line", required=True, ondelete="cascade")
    dealer_id = fields.Many2one("dyman.dealer", string="Dealer", required=True, ondelete="cascade")