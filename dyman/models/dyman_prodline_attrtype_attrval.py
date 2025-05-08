from odoo import api, fields, models

class ProductLineAttributeTypeAttributeValue(models.Model):
    _name = "dyman.prodline.attrtype.attrval"
    _description = "Dynamic product attribute type value"
    # The assignment of an attribute value to a product line and attribute type
    _sql_constraints = [('prodline_attrtype_attrval_uniq', 'unique(prodline_attrtype_id,attribute_value_id)', "Link between this attribute value and product line and attribute type already exists")]

    name = fields.Char(string="Name", related='attribute_value_id.name')
    prodline_attrtype_id = fields.Many2one("dyman.prodline.attrtype", string="Product line & Attribute type", required=True, ondelete="restrict")
    attribute_value_id = fields.Many2one("dyman.attribute.value", string="Attribute value", required=True, ondelete="restrict")
    filter_id = fields.Many2one("dyman.prodline.filter", string="Filter", ondelete="restrict")
    prodline_component_rule_ids = fields.One2many("dyman.prodline.component.rule", "prodline_attrtype_attrval_id", string="Component Rules")
    available_to_dealers = fields.Selection(selection=[('all', 'All dealers'), ('most', 'Most dealers'), ('selected', 'Selected dealers')], string="Available to", default="all")
    price_rule = fields.Selection(selection=[('fixed', 'Fixed'), ('component', 'From components')], required=True, default="component")
    price_trade = fields.Float('Trade price')
    price_retail = fields.Float('Retail price')
    dealer_restriction_ids = fields.One2many("dyman.attribute.dealer.restriction", "prodline_attrtype_attrval_id", string="Restrict to dealers")
