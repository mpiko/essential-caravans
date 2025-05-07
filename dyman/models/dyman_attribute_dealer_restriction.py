from odoo import api, fields, models

class AttributeDealerRestriction(models.Model):
    _name = "dyman.attribute.dealer.restriction"
    _description = "Dynamic product attribute dealer restriction"
    # An attribute value can be restricted to specific dealers.

    name = fields.Char(string='Name', related="dealer_id.name")
    prodline_attrtype_attrval_id = fields.Many2one("dyman.prodline.attrtype.attrval", string="Attribute value", required=True, ondelete="cascade")
    dealer_id = fields.Many2one("dyman.dealer", string="Dealer", required=True, ondelete="cascade")