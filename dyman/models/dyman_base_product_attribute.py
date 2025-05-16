from odoo import api, fields, models

class BaseProductAttribute(models.Model):
    _name = "dyman.base.product.attribute"
    _description = "The assignment of an attribute type and value pair to a base product"

    base_product_id = fields.Many2one("dyman.base.product", string="Base product", ondelete='cascade')
    attribute_type_id = fields.Many2one("dyman.attribute.type", string="Attribute type", ondelete='cascade')
    attribute_value_id = fields.Many2one("dyman.attribute.value", string="Attribute value", ondelete='cascade')
    source = fields.Selection(selection=[('base', 'Base'),('characteristic', 'Characteristic'),('default', 'Default')], string="Source")
