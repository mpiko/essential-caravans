from odoo import api, fields, models
from odoo.exceptions import ValidationError
import datetime

class BaseCharacteristicUpdate(models.Model):
    _name = "dyman.base.characteristic.update"
    _description = "Base product characteristic update rule"
    # A definition for a rule to update characteristc attributes on Base Products

    product_line_id = fields.Many2one("dyman.product.line", string="Product line")
    attribute_type_id = fields.Many2one("dyman.attribute.type", string="Attribute type", ondelete='cascade', domain="[('id', 'in', valid_attribute_type_ids)]")
    valid_attribute_type_ids = fields.One2many("dyman.attribute.type", string="Valid attributes", compute="_load_valid_attributes")
    attribute_value_id = fields.Many2one("dyman.attribute.value", string="Value", ondelete='cascade', domain="[('id', 'in', valid_attribute_value_ids)]")
    valid_attribute_value_ids = fields.One2many("dyman.attribute.value", string="Valid values", compute="_load_valid_values")
    include_where = fields.Char(string="Include where")
    only_where = fields.Char(string="Only where")
    not_where = fields.Char(string="Not where")
    base_characteristic_update_log_ids = fields.One2many("dyman.base.characteristic.update.log", "base_characteristic_update_id", string="Updates")
    last_applied = fields.Datetime(string="Last applied")

    @api.depends("product_line_id")
    def _load_valid_attributes(self):
        for record in self:
            attribute_list = []
            for prodline_attribute_type in record.product_line_id.prodline_attrtype_ids.filtered("characteristic"):
                attribute_list.append(prodline_attribute_type.attribute_type_id.id)
            record.valid_attribute_type_ids = attribute_list

    @api.depends("product_line_id", "attribute_type_id")
    def _load_valid_values(self):
        for record in self:
            if record.attribute_type_id:
                value_list = []
                prodline_attribute_types = self.product_line_id.prodline_attrtype_ids.search([('attribute_type_id', '=', record.attribute_type_id.id)])
                if len(prodline_attribute_types) != 1:
                    raise ValidationError("Product line should have exactly one attribute of type " + record.attribute_type_id.name)

                for value in prodline_attribute_types[0].prodline_attrtype_attrval_ids:
                    value_list.append(value.attribute_value_id.id)
                record.valid_attribute_value_ids = value_list
            else:
                record.valid_attribute_value_ids = False

    def apply(self):
        for base_prod in self.product_line_id.base_product_ids:
            update = True
            if self.include_where:
                update = False
                if self.include_where in base_prod.name:
                    update = True
                    if self.only_where:
                        update = False
                        if self.only_where in base_prod.name:
                            update = True
            if update ==True:
                if self.not_where:
                    if self.not_where in base_prod.name:
                        update = False
            if update ==True:
                self._apply_to(base_prod)

        timestamp = datetime.datetime.now()
        vals = {
                'base_characteristic_update_id': self.id,
                'applied_time': timestamp
                }
        self.env['dyman.base.characteristic.update.log'].create(vals)

        self.last_applied = timestamp

        return {'return':True, 'type': 'ir.actions.act_window_close'}
                
    def _apply_to(self, base_prod):

        existing_characteristics = self.env['dyman.base.product.attribute'].search([('base_product_id','=',base_prod.id), ('attribute_type_id','=',self.attribute_type_id.id)])

        for existing_characteristic in existing_characteristics:
            existing_characteristic.unlink()

        if self.attribute_value_id:

            vals = {
                    'base_product_id': base_prod.id,
                    'attribute_type_id': self.attribute_type_id.id,
                    'attribute_value_id': self.attribute_value_id.id,
                    'base': False,
                    'characteristic': True
                    }
            self.env['dyman.base.product.attribute'].create(vals)

