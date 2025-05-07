from odoo import api, fields, models

class BaseProduct(models.Model):
    _name = "dyman.base.product"
    _description = "Dynamic base product"
    # A base product is a combination of attribute values for each attribute type defined as 'base' against a particular product line

    name = fields.Char(string='Name', required=True)
    status = fields.Selection(selection=[('new', 'New'),('active', 'Active'),('invalid', 'Invalid'), ('removed', 'Removed')], string="Status", default="new")
    price_trade = fields.Float('Trade price')
    price_retail = fields.Float('Retail price')
    product_line_id = fields.Many2one("dyman.product.line", string="Product line", required=True, ondelete="cascade")
    base_product_attribute_ids = fields.One2many("dyman.base.product.attribute", "base_product_id", string="Attributes")
    base_material_ids = fields.One2many("dyman.base.material", "base_product_id", string="Materials (parts)")

    def Remove(self):
        if len(self.env['dyman_order'].search([('base_product_id', '=', self.id)])) == 0:
            self.unlink()
        else:
            self.status = 'removed'
