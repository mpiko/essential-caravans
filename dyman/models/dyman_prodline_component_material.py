from odoo import api, fields, models

class ProductLineComponentMaterial(models.Model):
    _name = "dyman.prodline.component.material"
    _description = "Dynamic product component material"
    # The assignment of a material (Product.Product) as beng available to a Product Line Component

    prodline_component_id = fields.Many2one("dyman.prodline.component", string="Product line component", ondelete="cascade")
    material_id = fields.Many2one("product.product", string="Material (Part)", ondelete="cascade")
    filter_id = fields.Many2one("dyman.prodline.filter", string="Filter", ondelete="restrict")