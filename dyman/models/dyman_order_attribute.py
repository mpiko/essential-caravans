from odoo import api, fields, models
from . import dyman_product_line

class OrderAttribute(models.Model):
    _name = "dyman.order.attribute"
    _description = ""
    # The assignment of an attribute type and value pair to an order

    order_id = fields.Many2one("dyman.order", string="Order", required=True, ondelete="cascade")
    sequence = fields.Integer(string="Sequence")
    attribute_type_id = fields.Many2one("dyman.attribute.type", string="Attribute type", domain="[('id', 'in', parent.valid_attrtype_ids)]", ondelete="restrict")
    attribute_type = fields.Char(string="Attribute type")
    attribute_value_id = fields.Many2one("dyman.attribute.value", string="Attribute value", domain="[('id', 'in', valid_attrval_ids)]", ondelete="restrict")
    attribute_value = fields.Char(string="Attribute value")
    valid_attrval_ids = fields.One2many('dyman.attribute.value',string="Valid attribute values",compute="_load_valid_attrvalues", store=False)

    @api.depends("attribute_type_id")
    def _load_valid_attrvalues(self):

        for record in self:
            record.valid_attrval_ids = record._get_valid_attrvalues()

    def _get_valid_attrvalues(self):
        attribute_value_id_list = []
    
        product = []
        
        for attribute in self.order_id.order_attribute_ids:
            product.append(dyman_product_line.AttributePair(attribute.attribute_type_id,attribute.attribute_value_id))
            
        prodline_attrtypes = self.env['dyman.prodline.attrtype'].search([('product_line_id', '=', self.order_id.product_line_id.id),('attribute_type_id', '=', self.attribute_type_id.id)])
        
        for prodline_attrtype in prodline_attrtypes:
            attribute_values = self.env['dyman.prodline.attrtype.attrval'].search([('prodline_attrtype_id', '=', prodline_attrtype.id)])
            for attribute_value in attribute_values:

                attribute_pair = dyman_product_line.AttributePair(prodline_attrtype.attribute_type_id,attribute_value.attribute_value_id)
            
                if self.order_id.product_line_id.validate_attribute_against_product(attribute_pair, product):
                    attribute_value_id_list.append(attribute_value.attribute_value_id.id)

        if len(attribute_value_id_list) == 0:
            attribute_value_id_list = False

        return attribute_value_id_list
    
    def write(self, vals):
        vals['attribute_type'] = self.attribute_type_id.name
        vals['attribute_value'] = self.attribute_value_id.name
        res = super(OrderAttribute, self).write(vals)
        return res