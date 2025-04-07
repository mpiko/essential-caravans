from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    trade_price = fields.Float('Trade price')
    nla = fields.Boolean('No longer available')
    