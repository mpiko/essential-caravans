from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ProductLineAttributeType(models.Model):
    _name = "dyman.prodline.attrtype"
    _description = "The assignment of an attribute type to a product line"
    _sql_constraints = [('prodline_attrtype_uniq', 'unique(product_line_id,attribute_type_id)', "Link between this attribute type and product line already exists")]

    name = fields.Char(string='Name', related="attribute_type_id.name")
    active = fields.Boolean(string='Active', default=True)
    product_line_id = fields.Many2one("dyman.product.line", string="Product line")
    attribute_type_id = fields.Many2one("dyman.attribute.type", string="Attribute type")
    sequence = fields.Integer(string="Sequence")
    base = fields.Boolean(string="Base?")
    characteristic = fields.Boolean(string="Characteristic?")
    required = fields.Boolean(string="Required?")
    prodline_attrtype_attrval_ids = fields.One2many("dyman.prodline.attrtype.attrval", "prodline_attrtype_id", string="Attribute Values")

    @api.constrains('base', 'derived_from')
    def _check_base_derived(self):
        for record in self:
            if record.base and record.derived_from:
                raise ValidationError("Base attributes can not be derived")

