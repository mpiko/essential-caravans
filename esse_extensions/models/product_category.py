# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = "product.category"

    sku_prefix = fields.Char(string="SKU Prefix", size=2)