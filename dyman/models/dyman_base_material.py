from odoo import api, fields, models

class BaseMaterial(models.Model):
    _name = "dyman.base.material"
    _description = "Base product material"
    # A base material is the assignment of a quantity of product.product against a component for a Base product, forming an item within a standard Bill of Materials.

    base_product_id = fields.Many2one("dyman.base.product", string="Base product", required=True, ondelete="cascade")
    component_id = fields.Many2one("dyman.component", string="Component", required=True, ondelete="restrict")
    material_id = fields.Many2one("product.product", string="Material (Part)", required=True, ondelete="restrict")
    quantity = fields.Float(string="Quantity", default=1)
