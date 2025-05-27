from odoo import fields, models
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    trade_price = fields.Float('Trade price')
    nla = fields.Boolean('No longer available')
    sku_prefix = fields.Char(string="SKU Prefix", related="categ_id.sku_prefix")
    sku = fields.Char(string="SKU")
    sku_added = fields.Boolean('SKU added')

    def update_sku(self):
        if not self.categ_id:
            raise ValidationError("Category must have a prefix set")

        if not self.categ_id.sku_prefix:
            raise ValidationError("Product must be assigned to a category")

        self.default_code = self.categ_id.sku_prefix + str(self.id)
        self.sku_added = True

