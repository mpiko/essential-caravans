import json

from xlwt.ExcelFormulaLexer import false_pattern

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ProductLine(models.Model):
    _name = "dyman.product.line"
    _description = "Dynamic product line"
    # A dynamic product line is a set of attributes and possible values, which can be used to define a dynamic product"

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    prodline_attrtype_ids = fields.One2many("dyman.prodline.attrtype", "product_line_id", string="Attributes")
    prodline_component_category_ids = fields.One2many("dyman.prodline.component.category", "product_line_id", string="Component categories")
    prodline_operation_ids = fields.One2many("dyman.prodline.operation", "product_line_id", string="Operations")
    base_product_ids = fields.One2many("dyman.base.product", "product_line_id", string="Base Products", domain="[('id', 'in', filtered_base_product_ids)]")
    base_product_filter = fields.Selection(selection=[('all', 'All'),('new', 'New'),('active', 'Active'),('invalid', 'Invalid'), ('removed', 'Removed')], string="Product status", default="active", store=False)
    filtered_base_product_ids = fields.One2many("dyman.base.product", "product_line_id", domain="[('status', '=', self.base_product_filter)]")
    prodline_filter_ids = fields.One2many("dyman.prodline.filter", "product_line_id", string="Filters")
    base_material_update_ids = fields.One2many("dyman.base.material.update", "product_line_id", string="Base material updates")
    prodline_warehouse_ids = fields.One2many("dyman.prodline.warehouse", "product_line_id", string="Warehouses")
    process_ids = fields.One2many("dyman.process", "product_line_id", string="Manufacturing processes", domain=[('order_id','=',False)])
    available_to_dealers = fields.Selection(selection=[('all', 'All dealers'), ('most', 'Most dealers'), ('selected', 'Selected dealers')], string="Available to", default="all")
    dealer_restriction_ids = fields.One2many("dyman.prodline.dealer.restriction", "product_line_id", string="Restrict to dealers")

    @api.depends("base_product_filter")
    def _filter_base_products(self):
        for product_line in self:
            base_product_list = []
            for base_product in self.env['dyman.base.product'].search([('product_line_id', '=', product_line._origin.id)]):
                if (product_line.base_product_filter == 'all') or (
                        base_product.status == product_line.base_product_filter):
                    base_product_list.append(base_product.id)
                if len(base_product_list) == 0:
                    product_line.filtered_base_product_ids = False
                else:
                    product_line.filtered_base_product_ids = base_product_list

    def action_update_base_products(self):
        #Check for removed attribute types and values
        for base_product in self.env['dyman.base.product'].search([('status', '!=', 'Removed')]):
            for base_product_attribute in self.env['dyman.base.product.attribute'].search([('base_product_id', '=', base_product.id)]):
                attribute_exists = False
                for product_line_attribute_type in self.prodline_attrtype_ids:
                    if product_line_attribute_type.attribute_type_id == base_product_attribute.attribute_type_id:
                        for product_line_attr_value in product_line_attribute_type.prodline_attrtype_attrval_ids:
                            if product_line_attr_value.attribute_value_id == base_product_attribute.attribute_value_id:
                                attribute_exists =  True
                                break
                if not attribute_exists:
                    base_product.Remove()

        #Check for new attribute types and values

        attributes = self.prodline_attrtype_ids.filtered("base").sorted("sequence")
        base_prods = self._get_base_products(attributes, 0)
        base_prods = self._restrict_base_products(base_prods)
        base_prods = self._retain_existing_base_prods(base_prods)

        if base_prods:
             for base_prod in base_prods:
                 attr_vals = []
                 for attr_val in base_prod:
                     vals = {
                             'base_product_id': self.id,
                             'attribute_type_id': attr_val.attribute_type_id.id,
                             'attribute_value_id': attr_val.attribute_value_id.id,
                             'base': True
                             }
                     attr_vals.append((0,0,vals))

                 name = _name_base_product(base_prod)
                 vals = {
                        'name': name,
                        'status': 'new',
                        'product_line_id': self.id,
                        'base_product_attribute_ids': attr_vals
                        }
                 self.env['dyman.base.product'].create(vals)

    def _get_base_products(self, attributes, attr_num, old_list=None):
        
        if old_list is None:
            old_list = []
            old_product = []
            old_list.append(old_product)

        new_list = []
        if len(attributes) > 0:
            for old_product in old_list:
                if len(attributes[attr_num].prodline_attrtype_attrval_ids) == 0:
                    raise ValidationError("Base attributes must have at least 1 value. "
                                        "Attribute '" + attributes[attr_num].attribute_type_id.name + "' does not have any allowable values")
                for attr_val in attributes[attr_num].prodline_attrtype_attrval_ids:
                    new_product = []
                    for old_val in old_product:
                        new_product.append(old_val)
                    
                    new_product.append(AttributePair(attr_val.prodline_attrtype_id.attribute_type_id,attr_val.attribute_value_id))

                    new_list.append(new_product)

            if attr_num+1 < len(attributes):
                new_list = self._get_base_products(attributes, attr_num+1, new_list)
        
        return new_list

    def _restrict_base_products(self, old_list):
        
        new_list = []
        
        for product in old_list:

            if self.validate_product(product):
                new_list.append(product)

        return new_list

    def _retain_existing_base_prods(self, new_list):
        
        for old_product in self.base_product_ids:
            # Make sure the old products have the full set of attributes
            for attribute in self.prodline_attrtype_ids.filtered("base"):
                match = False
                for old_attr in old_product.base_product_attribute_ids:
                    if old_attr.attribute_type_id == attribute.attribute_type_id:
                        match = True
                        break
                if not match:
                    break
            if match:
                match = False
                for new_product in new_list:
                    for old_attr in old_product.base_product_attribute_ids:
                        match = False
                        for new_attr in new_product:
                            if ((old_attr.attribute_type_id == new_attr.attribute_type_id) and (old_attr.attribute_value_id == new_attr.attribute_value_id)):
                                match = True
                                break
                        if not match:
                            break
                    if match:
                        break
            if match:
                old_product.name = _name_base_product(new_product)
                new_list.remove(new_product)
            else:
                old_product.unlink()

        return new_list

    def launch_update_base_materials(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Base Material Update',
            'res_model': 'dyman.base.material.update',
            'view_mode': 'form'
        }

    def launch_update_base_characteristics(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Base Characteristic Update',
            'res_model': 'dyman.base.characteristic.update',
            'view_mode': 'form'
        }

    def get_component_operation(self, component):
        
        prodline_components = self.env['dyman.prodline.component'].search([('product_line_id','=',self.id), ('component_id','=',component.id)])

        if len(prodline_components) == 0:
            raise ValidationError("Component " + component.name +" not found on " + self.name)
        
        if len(prodline_components) > 1:
            raise ValidationError("Multiple instances of component " + component.name +" found on " + self.name)                
            
        return prodline_components[0].operation_id

    def validate_product(self, product):
        #product is a list of AttributePairs
        
        valid = True
        for attribute_pair in product:
            valid = self.validate_attribute_against_product(attribute_pair, product)
            
            if not valid:
                break
        
        return valid
    
    def validate_attribute_against_product(self, attribute_pair, product):
        valid = True
        found_attr_type = False
        found_attr_val = False

        for prodline_attrtype in self.prodline_attrtype_ids:
            if prodline_attrtype.attribute_type_id == attribute_pair.attribute_type_id:
                found_attr_type = True
                for prodline_attrtype_attr_val in prodline_attrtype.prodline_attrtype_attrval_ids:
                    if prodline_attrtype_attr_val.attribute_value_id == attribute_pair.attribute_value_id:
                        found_attr_val = True
                        if prodline_attrtype_attr_val.filter_id:
                            valid = self.apply_filter(prodline_attrtype_attr_val.filter_id, product)
                    if found_attr_val:
                        break
            if found_attr_type:
                break
        
        return valid

    def apply_filter(self, filter, product):
        
        valid = True
        
        if filter.apply_to_filter_id:
            valid = self.apply_filter(filter.apply_to_filter_id, product)

        if valid:
            if filter.application_method == "only":
                valid = self.check_product_for_filter_match(filter, product)

            if filter.application_method == "not":
                valid = not self.check_product_for_filter_match(filter, product)

        else:
            if filter.application_method == "also":
                valid = self.check_product_for_filter_match(filter, product)

        return valid
    
    def check_product_for_filter_match(self, filter, product):
        included = False
        for attribute_pair in product:
            if attribute_pair.attribute_type_id == filter.attribute_type_id:
                match filter.filter_rule:
                    case "in":
                        if filter.filter_string.casefold() in attribute_pair.attribute_value_id.name.casefold():
                            included = True
                    case "start":
                        if attribute_pair.attribute_value_id.name.casefold().startswith(filter.filter_string.casefold()):
                            included = True
                    case "exact":
                        if filter.filter_string.casefold() == attribute_pair.attribute_value_id.name.casefold():
                            included = True
                break
        return included
    
    def get_valid_warehouse_ids(self):
        warehouse_id_list = []

        for warehouse in self.prodline_warehouse_ids:
            warehouse_id_list.append(warehouse.warehouse_id.id)
        
        return warehouse_id_list
    
def _name_base_product(product):

    name = ""
    for attr_val in product:
        name = name + " " + attr_val.attribute_value_id.name
    
    return name.lstrip()

class AttributePair():
    def __init__(self, attribute_type, attribute_value):
        self.attribute_type_id = attribute_type
        self.attribute_value_id = attribute_value
