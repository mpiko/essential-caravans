from odoo import api, fields, models

class ProdlineComponentRule(models.Model):
    _name = "dyman.prodline.component.rule"
    _description = "Dynamic product component rule"
    # A component rule is used to add, remove or alter the product and/or quantity for a component of an order, based on an attribute of that order.

    prodline_attrtype_attrval_id = fields.Many2one("dyman.prodline.attrtype.attrval", string="Attribute", ondelete="cascade")
    component_id = fields.Many2one("dyman.component", string="Component",  domain="[('id', 'in', valid_component_ids)]", ondelete="cascade")
    material_id = fields.Many2one("product.product", string="Material (Part)", ondelete="restrict")
    quantity_operation = fields.Selection(selection=[('new', 'New Value'),('add', 'Add'),('subtract', 'Subtract'),('multiply', 'Multiply'),('divide', 'Divide')], string='How to apply quantity', default='new') 
    quantity = fields.Float(string="Quantity", default=1)
    valid_component_ids = fields.One2many('dyman.component',string="Valid components",compute="_load_valid_components")

    @api.depends("prodline_attrtype_attrval_id")
    def _load_valid_components(self):
        for record in self:
            record.valid_component_ids = record._get_valid_components()

    def _get_valid_components(self):
        component_id_list = []

        for component in self.prodline_attrtype_attrval_id.prodline_attrtype_id.product_line_id.prodline_component_ids:
            component_id_list.append(component.component_id.id)

        if len(component_id_list) == 0:
            component_id_list = False

        return component_id_list