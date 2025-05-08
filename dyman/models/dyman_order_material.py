from odoo import api, fields, models

class OrderMaterial(models.Model):
    _name = "dyman.order.material"
    _description = "Dynamic product order material"
    # An order material is the assignment of a quantity of product.product against a component for an order, forming an item the Bill of Materials for that Order.

    order_id = fields.Many2one("dyman.order", string="Order", required=True, ondelete="cascade")
    component_id = fields.Many2one("dyman.component", string="Component", required=True, ondelete="restrict")
    operation_id = fields.Many2one("dyman.operation", string="Operation", required=True, ondelete="restrict")
    material_id = fields.Many2one("product.product", string="Material (part)", required=True, ondelete="restrict")
    quantity = fields.Float(string="Quantity", default=1)
    source = fields.Selection(selection=[('base', 'Base product material'),('rule', 'Component rule'),('manual', 'Manual selection')], string="Source", required=True)