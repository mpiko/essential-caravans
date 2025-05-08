from odoo import api, fields, models

class ProductLineWarehouse(models.Model):
    _name = "dyman.prodline.warehouse"
    _description = "Dynamic product line warehouse"
    # The assignment of a warehouse to a product line, to resolve a many to many relationship

    name = fields.Char(string="Warehouse", related="warehouse_id.name", store=True)
    product_line_id = fields.Many2one("dyman.product.line", string="Product line", required=True, ondelete="cascade")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True, ondelete="restrict")
    stock_picking_type_id = fields.Many2one("stock.picking.type", string='Dynamic Manufacturing Type', required=True, ondelete="restrict")
    wip_location_id = fields.Many2one("stock.location", string='WIP location', required=True, ondelete="restrict")
