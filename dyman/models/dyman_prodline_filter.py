from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ProductLineFilter(models.Model):
    _name = "dyman.prodline.filter"
    _description = "Dynamic product filter"
    # A filter defines a pattern matching rule, which can be used for defining a subset of products

    name = fields.Char(string='Name', compute="_get_name", store=True)
    product_line_id = fields.Many2one("dyman.product.line", string="Product line", required=True, ondelete="cascade")
    apply_to_filter_id = fields.Many2one("dyman.prodline.filter", string="Apply to", domain="[('id', 'in', valid_filter_ids)]", ondelete="restrict")
    valid_filter_ids = fields.One2many(string="Valid filters", related="product_line_id.prodline_filter_ids")
    application_method = fields.Selection(selection=[('only', 'Only where'),('not', 'Not where'),('also', 'Also where')], string='How to apply filter', compute='_set_application_method', store=True)
    application_method_all = fields.Selection(selection=[('only', 'Only where'),('not', 'Not where'),('also', 'Also where')], string='How to apply filter')
    application_method_limited = fields.Selection(selection=[('only', 'Only where'),('not', 'Not where')], string='How to apply filter')
    attribute_type_id = fields.Many2one("dyman.attribute.type", string="Attribute type", domain="[('id', 'in', valid_attribute_type_ids)]", required=True, ondelete="restrict")
    valid_attribute_type_ids = fields.One2many('dyman.attribute.type',string="Valid attribute types",compute="_load_valid_attribute_types")
    filter_rule = fields.Selection(selection=[('in', 'Includes'), ('start', "Begins with"), ('exact', 'Exact match')], string='Rule', required=True)
    filter_string = fields.Char(string='Value', required=True)
    
    @api.depends('apply_to_filter_id','application_method','attribute_type_id','filter_rule','filter_string')
    def _get_name(self):
        for record in self:
            record.name = record._create_name()       
    
    def _create_name(self):
        
        if self.apply_to_filter_id:
            
            name = self.apply_to_filter_id.name
            
            match self.application_method:
                case 'only':
                    name = name + " but only "
                case 'not':
                    name = name + " but not "
                case 'also':
                    name = name + " and also "
            
            if self.attribute_type_id:
                name = name + "where " + self.attribute_type_id.name
            else:
                name = name + "where unspecified attribute "
            
        else:
            if self.attribute_type_id:
                name = "Where " + self.attribute_type_id.name
            else:
                name = "Where unspecified attribute "

        match self.filter_rule:
            case 'in':
                if self.application_method == 'not':
                    name = name + " does not contain "
                else:
                    name = name + " contains "
            case 'start':
                if self.application_method == 'not':
                    name = name + " does not begin with "
                else:
                    name = name + " begins with "
            case 'exact':
                if self.application_method == 'not':
                    name = name + " does not equal "
                else:
                    name = name + " equals "                       
        
        if self.filter_string:
            name = name + self.filter_string
        else:
            name = name + " unspecified string"
        
        return name

    @api.depends('apply_to_filter_id', 'application_method_all','application_method_limited')
    def _set_application_method(self):
        for record in self:
            record.application_method = record._get_application_method()

    def _get_application_method(self):
        if self.apply_to_filter_id:
            method = self.application_method_all
        else:
            method = self.application_method_limited
        return method
    
    @api.depends("product_line_id")
    def _load_valid_attribute_types(self):
        for record in self:
            record.valid_attribute_type_ids = record._get_valid_attribute_types()

    def _get_valid_attribute_types(self):
        attribute_type_id_list = []

        for attribute_type in self.product_line_id.prodline_attrtype_ids:
            attribute_type_id_list.append(attribute_type.attribute_type_id.id)

        if len(attribute_type_id_list) == 0:
            attribute_type_id_list = False

        return attribute_type_id_list
    
    @api.onchange('apply_to_filter_id')
    def _check_for_circular_reference(self):
        for record in self:
            if record._circular_reference(record._origin):
               raise ValidationError("Applying this filter would create a circular reference")
 
    def _circular_reference(self, filter):

        circular = False

        if self.apply_to_filter_id:
            if self.apply_to_filter_id == filter:
                circular = True
            else:
                circular = self.apply_to_filter_id._circular_reference(filter)

        return circular