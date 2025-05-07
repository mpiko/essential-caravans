from odoo import api, fields, models
from odoo.exceptions import ValidationError
from . import dyman_product_line

class Order(models.Model):
    _name = "dyman.order"
    _description = "Dynamic manufacturing order"

    name = fields.Char(string='Name', required=True)
    dealer_id = fields.Many2one("dyman.dealer", string = "Dealer", required=True, ondelete="restrict")
    product_line_id = fields.Many2one("dyman.product.line", string="Product line", required=True)
    base_product_id = fields.Many2one("dyman.base.product", string="Base product", ondelete="restrict")
    order_type = fields.Selection(selection=[('stock', 'Stock'),('customer', 'Customer')], string="Order type", required=True, default='stock')
    customer_name = fields.Char(string="Customer name")
    customer_address = fields.Text(string="Address")
    customer_phone = fields.Char(string="Mobile")
    customer_email = fields.Char(string="email")
    order_status = fields.Selection(selection=[('draft', 'Draft/Incomplete'),('returned', 'Returned'),('submitted', 'Submitted'),('accepted', 'Accepted'),('signed', 'Signed off'),('cancelled', 'Cancelled')], string="Order status", default='draft')
    build_month = fields.Many2one("dyman.build.month", string = "Build month", ondelete="restrict")
    order_attribute_ids = fields.One2many("dyman.order.attribute", "order_id", string="Attributes")
    available_base_product_ids = fields.One2many("dyman.base.product", string="Available base products", compute="_load_available_base_products")
    valid_attrtype_ids = fields.One2many('dyman.attribute.type',string="Valid attribute types", compute="_load_valid_attrtypes")
    order_material_ids = fields.One2many("dyman.order.material", "order_id", string="Materials")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", domain="[('id', 'in', valid_warehouse_ids)]", ondelete="restrict")
    stock_picking_type_id = fields.Many2one("stock.picking.type", string='Dynamic Manufacturing Type', ondelete="restrict")
    wip_location_id = fields.Many2one("stock.location", string='WIP location', ondelete="restrict")
    valid_warehouse_ids = fields.One2many("stock.location", string="Valid warehouses", compute="_load_valid_warehouse_ids", store=False)
    source_process_id = fields.Many2one("dyman.process", string="Source process", domain="[('id', 'in', valid_process_ids)]", ondelete="restrict")
    valid_process_ids = fields.One2many(string="Valid processes", related="product_line_id.process_ids", store=False)
    build_process_id = fields.Many2one("dyman.process", string="Build process", domain="[('id', 'in', valid_process_ids)]", ondelete="restrict")
    process_operation_ids = fields.One2many(string="Operations", related="build_process_id.process_operation_ids")
    schedule_date_online = fields.Date(string="Scheduled on-line date")
    


    @api.depends("dealer_id", "product_line_id", "order_attribute_ids")
    def _load_available_base_products(self):
        for order in self:
            order.available_base_product_ids = self._get_available_base_products()

    def _get_available_base_products(self):
        base_products = []
        if self.product_line_id and self.dealer_id:

            base_products = self.dealer_id.available_base_product_ids.filtered(
                lambda r: r.product_line_id == self.product_line_id).mapped('id')

            for attribute in self.order_attribute_ids:
                base_products = self.env['dyman.base.product.attribute'].search(
                    [('base_product_id.id', "in", base_products),
                     ('attribute_type_id', "=", attribute.attribute_type_id.id),
                     ('attribute_value_id', "=", attribute.attribute_value_id.id)]).mapped('base_product_id.id')

        if len(base_products) == 0:
            base_products = False

        return base_products

    @api.depends("product_line_id")
    def _load_valid_attrtypes(self):
        self.valid_attrtype_ids = self._get_valid_attrtypes()

    def _get_valid_attrtypes(self):
        
        attribute_type_id_list = []

        if self.product_line_id:
        
            attribute_types = self.env['dyman.prodline.attrtype'].search([('product_line_id', '=', self.product_line_id.id)])
                
            for attribute_type in attribute_types:
                attribute_type_id_list.append(attribute_type.attribute_type_id.id)

        if len(attribute_type_id_list) == 0:
            attribute_type_id_list = False

        return attribute_type_id_list
        
    def _validate_attributes(self):
    
        product = []
        
        for attribute in self.order_attribute_ids:
            product.append(dyman_product_line.AttributePair(attribute.attribute_type_id,attribute.attribute_value_id))

        for attribute in self.order_attribute_ids:

            attribute_pair = dyman_product_line.AttributePair(attribute.attribute_type_id,attribute.attribute_value_id)

            if not self.product_line_id.validate_attribute_against_product(attribute_pair, product):
                raise ValidationError(attribute_pair.attribute_value_id.name + " is not a valid " + attribute_pair.attribute_type_id.name + " due to filter rules" )

    @api.depends("product_line_id")
    def _load_valid_warehouse_ids(self):

        if self.product_line_id:
            valid_warehouse_ids = self.product_line_id.get_valid_warehouse_ids()
        else:
            valid_warehouse_ids = []
        
        if len(valid_warehouse_ids) == 0:
            valid_warehouse_ids = False

        self.valid_warehouse_ids = valid_warehouse_ids

    def create(self, vals):
        self._validate_attributes()
        return super(Order, self).create(vals)
    
    def write(self, vals):
        res = super(Order, self).write(vals)
        self._validate_attributes()
        return res

    def update_materials(self):

        for material in self.order_material_ids:
            material.unlink()

        base_products = self.env['dyman.base.product'].search([('product_line_id', '=', self.product_line_id.id)])
        for base_product in base_products:
            match = True
            for base_attribute in base_product.base_product_attribute_ids:
                if len(self.env['dyman.order.attribute'].search([('order_id', '=', self.id),('attribute_type_id', '=', base_attribute.attribute_type_id.id),('attribute_value_id', '=', base_attribute.attribute_value_id.id)])) == 0:
                    match = False
                    break
            
            if match:
                for base_material in base_product.base_material_ids:
                    vals = {
                            'order_id': self.id,
                            'component_id': base_material.component_id.id,
                            'material_id': base_material.material_id.id,
                            'quantity': base_material.quantity
                            }
                    self.env['dyman.order.material'].create(vals)
                break

        if not match:
            raise ValidationError("No matching Base Product found for order " + self.name )

        self._apply_component_rules()

    def _apply_component_rules(self):

        for order_attribute in self.order_attribute_ids:
            for attribute_type in self.env['dyman.prodline.attrtype'].search([('product_line_id', '=', self.product_line_id.id), ('attribute_type_id', '=', order_attribute.attribute_type_id.id)]):
                for prodline_attribute in self.env['dyman.prodline.attrtype.attrval'].search([('prodline_attrtype_id', '=', attribute_type.id), ('attribute_value_id', '=', order_attribute.attribute_value_id.id)]):
                    for component_rule in prodline_attribute.prodline_component_rule_ids:
                        
                        operation = self.product_line_id.get_component_operation(component_rule.component_id)

                        existing_materials = self.env['dyman.order.material'].search([('order_id', '=', self.id), ('component_id', '=', component_rule.component_id.id)])
                        
                        if len(existing_materials) == 0:
                            vals = {
                                    'order_id': self.id,
                                    'component_id': component_rule.component_id.id,
                                    'material_id': component_rule.material_id.id,
                                    'quantity': component_rule.quantity
                                    }
                            self.env['dyman.order.material'].create(vals)

                        else:
                            for existing_material in existing_materials:
                                
                                match component_rule.quantity_operation:
                                        case 'new':
                                            existing_material.quantity = component_rule.quantity
                                        case 'add':
                                            existing_material.quantity = existing_material.quantity+component_rule.quantity
                                        case 'subtract':
                                            existing_material.quantity = existing_material.quantity-component_rule.quantity
                                        case 'multiply':
                                            existing_material.quantity = existing_material.quantity*component_rule.quantity
                                        case 'divide':
                                            existing_material.quantity = existing_material.quantity/component_rule.quantity

                                if (not component_rule.material_id) and (existing_material.quantity ==0):
                                    existing_material.unlink()
                                else:
                                    existing_material.operation_id = operation
                                    if component_rule.material_id:
                                        existing_material.material_id = component_rule.material_id
                                    
    def manufacture(self):

        if not self.warehouse_id:
            raise ValidationError("Please specify a warehouse to manufacture in")    

        prodline_warehouses = self.env['dyman.prodline.warehouse'].search([('product_line_id', '=', self.product_line_id.id),('warehouse_id', '=', self.warehouse_id.id)])
        
        if len(prodline_warehouses) == 0:
            raise ValidationError("Warehouse " + self.warehouse_id.name + " is not currently attached to the Product Line " + self.product_line_id.name)    

        if len(prodline_warehouses) > 1:
            raise ValidationError("Warehouse " + self.warehouse_id.name + " is currently duplicated on Product Line " + self.product_line_id.name)    

        if not prodline_warehouses[0].stock_picking_type_id:
            raise ValidationError("Warehouse " + self.warehouse_id.name + " on Product Line " + self.product_line_id.name + " does not have an operation defined for dynamic manufacturing")    
        else:
            self.stock_picking_type_id = prodline_warehouses[0].stock_picking_type_id.id

        if not prodline_warehouses[0].wip_location_id:
            raise ValidationError("Warehouse " + self.warehouse_id.name + " on Product Line " + self.product_line_id.name + " does not have a WIP location defined")    
        else:
            self.wip_location_id = prodline_warehouses[0].wip_location_id.id

        product = []
        
        for attribute in self.order_attribute_ids:
            product.append(dyman_product_line.AttributePair(attribute.attribute_type_id,attribute.attribute_value_id))
        
        if not self.source_process_id:
            process = self._get_manufacturing_process(product)
            if process:
                self.source_process_id = process.id

        self._create_build_process(product)

        self._add_prerequisites_to_operations()

        if self.build_process_id.check_for_circular_reference():
            raise ValidationError("The build process includes a circular reference")    

        exit_operations = self.build_process_id.get_exit_operations()
        if len(exit_operations) > 1:
            raise ValidationError("The build process has multiple exit operations")
        else:
            exit_operations[0].final = True

        self._add_operations_to_materials()

        self._update_operations_status()

        for process in self.process_operation_ids:
            process.create_stock_move()
        
        # vals = {
        #         'dyman_order_id': self.id, 
        #         'scheduled_date' : datetime.datetime.now(),
        #         'picking_type_id': self.warehouse.dyman_picking_type_id.id
        #         }      

        # manufacturing_order = self.env['stock.picking'].create(vals)      

        # for material in self.order_material_ids:
        #     vals = {
        #             'name': _('New'),
        #             'picking_id': manufacturing_order.id,
        #             'product_id': material.material_id.id,
        #             'product_uom_qty': material.quantity,
        #             'location_id': manufacturing_order.location_id.id,
        #             'location_dest_id': manufacturing_order.location_dest_id.id
        #             }
            
        #     self.env['stock.move'].create(vals)                        
        
        # manufacturing_order.action_confirm()

        # for line in manufacturing_order.move_ids:
        #     line.write({'quantity': line.product_uom_qty })

        # manufacturing_order.button_validate()
    
    def _get_manufacturing_process(self, product):

        match_count = 0
        for process in self.env['dyman.process'].search([('product_line_id', '=', self.product_line_id.id),('apply_to_warehouse_id', '=', self.warehouse_id.id),('order_id', '=', False)]):
            if self.product_line_id.apply_filter(process.apply_to_filter_id, product):
                match_count = match_count+1

        if match_count > 0:
            if match_count > 1:
                raise ValidationError("There are multiple processes for Warehouse " + self.warehouse_id.name + " on Product Line " + self.product_line_id.name + " with filters which could apply to this order")
            else:
                return process
        else:
            for process in self.env['dyman.process'].search([('product_line_id', '=', self.product_line_id.id),('apply_to_warehouse_id', '=', False),('apply_to_filter_id', '!=', False),('order_id', '=', False)]):
                if self.product_line_id.apply_filter(process.apply_to_filter_id, product):
                    match_count = match_count+1

            if match_count > 0:
                if match_count > 1:
                    raise ValidationError("There are multiple processes on Product Line " + self.product_line_id.name + " with filters which could apply to this order")
                else:
                    return process
                
            else:
                for process in self.env['dyman.process'].search([('product_line_id', '=', self.product_line_id.id),('apply_to_warehouse_id', '=', self.warehouse_id.id),('apply_to_filter_id', '=', False),('order_id', '=', False)]):
                    match_count = match_count+1

                if match_count > 0:
                    if match_count > 1:
                        raise ValidationError("There are multiple processes for Warehouse " + self.warehouse_id.name + " on Product Line " + self.product_line_id.name)
                    else:
                        return process
                    
                else:
                    for process in self.env['dyman.process'].search([('product_line_id', '=', self.product_line_id.id),('apply_to_warehouse_id', '=', False),('apply_to_filter_id', '=', False),('order_id', '=', False)]):
                        match_count = match_count+1

                    if match_count > 0:
                        if match_count > 1:
                            raise ValidationError("There are multiple default processes for Product Line " + self.product_line_id.name)
                        else:
                            return process     

                    else:
                        raise ValidationError("There is no matching process for this order")

    def _create_build_process(self, product):
        
        vals = {
                'order_id': self.id,
                'product_line_id': self.product_line_id.id
                }

        self.build_process_id = self.env['dyman.process'].create(vals)

        for source_operation in self.source_process_id.process_operation_ids:
            include_operation = True
            if source_operation.exclude_filter_id:
                if self.product_line_id.apply_filter(source_operation.exclude_filter_id, product):
                    include_operation = False

            if include_operation:
                vals = {
                        'process_id': self.build_process_id.id,
                        'operation_id': source_operation.operation_id.id
                        }                                                           

                build_operation = self.env['dyman.process.operation'].create(vals)

                for component in source_operation.component_process_operation_ids:
                    vals = {
                            'component_id': component.component_id.id,
                            'process_operation_id': build_operation.id
                            }
                    self.env['dyman.component.process.operation'].create(vals)

    def _add_operations_to_materials(self):
        
        for material in self.order_material_ids:
            operations = self.build_process_id.get_component_operations(material.component_id)
            if len(operations) == 0:
                raise ValidationError("There is no operation associated with component " + material.component_id.name)
            elif len(operations) > 1:
                raise ValidationError("There are " + str(len(operations)) + " operations associated with component " + material.component_id.name)
            else:
                material.operation_id = operations[0]

    def _add_prerequisites_to_operations(self):

        for operation in self.build_process_id.process_operation_ids:
            source_operations = self.env['dyman.process.operation'].search([('process_id', '=', self.source_process_id.id), ('operation_id', '=', operation.operation_id.id)])
            if len(source_operations) == 0:
                raise ValidationError("Operation " + operation.operation_id.name + " does not exist on process " +  self.source_process_id.name)
            elif len(source_operations) > 1:
                raise ValidationError("There are " + str(len(source_operations)) + " instances of operation " + operation.operation_id.name + " on process " + self.source_process_id.name)
            else:
                source_operation = source_operations[0]

            for prerequisite_source in source_operation.prerequisite_process_operation_ids:
                for prerequisite in self._get_prerequisite_operations(prerequisite_source):
                    if len(self.env['dyman.process.operation.prerequisite'].search([('process_operation_id','=',operation.id),('prerequisite_process_operation_id','=',prerequisite.id)])) == 0:
                        vals = {
                                'process_operation_id': operation.id,
                                'prerequisite_process_operation_id': prerequisite.id
                                }
                        self.env['dyman.process.operation.prerequisite'].create(vals)

    def _get_prerequisite_operations(self, prerequisite):
        
        prerequisite_operations = []
        for prerequisite_operation in self.env['dyman.process.operation'].search([('process_id', '=', self.build_process_id.id), ('operation_id', '=', prerequisite.prerequisite_process_operation_id.operation_id.id)]):
            prerequisite_operations.append(prerequisite_operation)
        
        if len(prerequisite_operations) == 0:
            for prerequisite_source in prerequisite.prerequisite_process_operation_id.prerequisite_process_operation_ids:
                for prerequisite in self._get_prerequisite_operations(prerequisite_source):
                    prerequisite_operations.append(prerequisite)
        
        return prerequisite_operations
    
    def _update_operations_status(self):

        for operation in self.build_process_id.process_operation_ids:
            operation.update_status()