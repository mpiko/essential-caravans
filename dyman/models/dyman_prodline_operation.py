from odoo import api, fields, models

class ProductLineOperation(models.Model):
    _name = "dyman.prodline.operation"
    _description = "Dynamic product line operation"
    # The assignment of an operation to a product line

    product_line_id = fields.Many2one("dyman.product.line", string="Product line", required=True, ondelete="cascade")
    operation_id = fields.Many2one("dyman.operation", string="Operation", required=True, ondelete="restrict")