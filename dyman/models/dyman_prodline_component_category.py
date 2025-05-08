from odoo import api, fields, models

class ProductLineComponentCategory(models.Model):
    _name = "dyman.prodline.component.category"
    _description = "Dynamic product line component category"
    # The assignment of a component category to a product line

    name = fields.Char(string='Name', related="component_category_id.name")
    product_line_id = fields.Many2one("dyman.product.line", string="Product line", ondelete="cascade")
    component_category_id = fields.Many2one("dyman.component.category", string="Component category", ondelete="cascade")
    include_on_spec_report = fields.Boolean(string="Include on spec sheet", default=True)
    component_ids = fields.One2many("dyman.prodline.component", "product_component_category_id", string="Components")

