# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = "product.category"

    sku_prefix = fields.Char(string="SKU Prefix", size=2)

    @api.depends('sku_prefix')
    def _compute_display_name(self):
        for record in self:
            if record.sku_prefix:
                record.display_name = "[" + record.sku_prefix + "] " + record.name
            else:
                record.display_name = record.name