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
    filter_id = fields.Many2one("dyman.prodline.filter", string="Filter", ondelete="restrict")
    sequence = fields.Integer(string="Sequence")
    base = fields.Boolean(string="Base?")
    characteristic = fields.Boolean(string="Characteristic?")
    required = fields.Boolean(string="Required?")
    derived_from_id = fields.Many2one("dyman.prodline.attrtype", string="Derived from", ondelete="restrict", domain="[('id', 'in', valid_derived_from_ids)]")
    valid_derived_from_ids = fields.One2many("dyman.prodline.attrtype", string="Valid attributes", compute="_load_valid_derived_from_ids")
    prodline_attrtype_attrval_ids = fields.One2many("dyman.prodline.attrtype.attrval", "prodline_attrtype_id", string="Attribute Values")

    @api.constrains('base', 'characteristic')
    def _check_base_characteristic(self):
        for record in self:
            if record.base and record.characteristic:
                raise ValidationError("Base attributes can not be characteristics")

    @api.depends('product_line_id')
    def _load_valid_derived_from_ids(self):
        for record in self:
            ids = record.product_line_id.prodline_attrtype_ids.filtered(
                lambda r: (r.id != record.id) and (not r.derived_from_id) and (r.base or r.characteristic)).mapped('id')
            if len(ids) == 0:
                record.valid_derived_from_ids = False
            else:
                record.valid_derived_from_ids = ids