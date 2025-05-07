from odoo import api, fields, models

class Process(models.Model):
    _name = "dyman.process"
    _description = "Dynamic manufacturing process"
    # A process is a sequence of operations to manufacture an order

    name = fields.Char(string='Name', compute="_get_name", store=True)
    order_id = fields.Many2one("dyman.order", string="Order", ondelete="cascade")
    product_line_id = fields.Many2one("dyman.product.line", string="Product line", ondelete="cascade")
    apply_to_filter_id = fields.Many2one("dyman.prodline.filter", string="Apply to filter", domain="[('id', 'in', valid_filter_ids)]", ondelete="restrict")
    valid_filter_ids = fields.One2many(string="Valid filters", related="product_line_id.prodline_filter_ids", store=False)
    apply_to_warehouse_id = fields.Many2one("stock.warehouse", string="Apply to warehouse", domain="[('id', 'in', valid_warehouse_ids)]", ondelete="restrict")
    valid_warehouse_ids = fields.One2many("stock.warehouse", string="Valid warehouses", compute="_load_valid_warehouse_ids", store=False)
    process_operation_ids = fields.One2many("dyman.process.operation", "process_id", string="Operations")

    @api.depends('order_id', 'product_line_id', 'apply_to_filter_id','apply_to_warehouse_id')
    def _get_name(self):
        for record in self:
            record.name = record._create_name()       

    def _create_name(self):

        if self.order_id:
            name = "Build process for order " + self.order_id.name
        else:
            if self.product_line_id:
                product_name = self.product_line_id._origin.name
            else:
                product_name = "Unspecified Product"


            if self.apply_to_filter_id:
                name = "Process for " + product_name + " " + self.apply_to_filter_id.name 
            else:
                name = "Default process for " + product_name

            name = name + " in "

            if self.apply_to_warehouse_id:
                name = name + self.apply_to_warehouse_id.name
            else:
                name = name + " ALL warehouses"
        
        return name
    
    @api.depends("product_line_id")
    def _load_valid_warehouse_ids(self):
        self.valid_warehouse_ids = self.product_line_id._origin.get_valid_warehouse_ids()

    def check_for_circular_reference(self):
        circular = False
        for operation in self.process_operation_ids:
            if operation.check_circular_reference(operation):
                circular = True
                break
        
        return circular
    
    def get_exit_operations(self):
        exit_operations = []
        for check_operation in self.process_operation_ids:
            operation_exits = True
            for operation in self.process_operation_ids:
                for prerequisite in operation.prerequisite_process_operation_ids:
                    if prerequisite.prerequisite_process_operation_id == check_operation:
                        operation_exits = False
                        break
                if operation_exits == False:
                    break
            if operation_exits:
                exit_operations.append(operation)
        return exit_operations
    
    def get_component_operations(self, component):
        component_operations = []
        for operation in self.process_operation_ids:
            for operation_component in operation.component_process_operation_ids:
                if operation_component.component_id == component:
                    component_operations.append(operation.operation_id)
        return component_operations