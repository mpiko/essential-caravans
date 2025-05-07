from odoo import api, fields, models, _
import datetime

class ProcessOperation(models.Model):
    _name = "dyman.process.operation"
    _description = "Dynamic manufacturing process operation"
    # The assignment of an operation to a process

    name = fields.Char(string="Name", related="operation_id.name")
    process_id = fields.Many2one("dyman.process", string="Process", required=True, ondelete="cascade")
    operation_id = fields.Many2one("dyman.operation", string="Operation", required=True, ondelete="restrict")
    exclude_filter_id = fields.Many2one("dyman.prodline.filter", string="Exclude filter", domain="[('id', 'in', valid_filter_ids)]", ondelete="restrict")
    valid_filter_ids = fields.One2many(string="Valid filters", related="process_id.product_line_id.prodline_filter_ids", store=False)
    prerequisite_process_operation_ids = fields.One2many("dyman.process.operation.prerequisite", "process_operation_id", string="Pre-requisites")
    component_process_operation_ids = fields.One2many("dyman.component.process.operation", "process_operation_id", string="Components")
    final = fields.Boolean(string="Final?")
    status = fields.Selection(selection=[('waiting', 'Waiting'),('ready', 'Ready'),('started', 'Started'),('completed', 'Completed')], string="Status", default='waiting')
    started = fields.Datetime(string="Started")
    completed = fields.Datetime(string="Completed")
    stock_picking_id = fields.Many2one("stock.picking", string="Stock move", ondelete="restrict")

    def check_circular_reference(self, process_operation):

        circular = False

        for prerequisite in self.prerequisite_process_operation_ids:
            if prerequisite.prerequisite_process_operation_id == process_operation:
                circular = True
            else:
                circular = prerequisite.prerequisite_process_operation_id.check_circular_reference(process_operation)

        return circular   

    def update_status(self):

        if self.status == "waiting":
            ready = True
            for prerequisite in self.prerequisite_process_operation_ids:
                prerequisite.prerequisite_process_operation_id.update_status()
                if prerequisite.prerequisite_process_operation_id.status != "completed":
                    ready = False
                    break
            if ready:
                self.status = "ready"

    def create_stock_move(self):
        
        for material in self.env['dyman.order.material'].search([('order_id','=',self.process_id.order_id.id),('operation_id','=',self.operation_id.id)]):
            if not self.stock_picking_id:
                vals = {
                        'name': self.process_id.order_id.name + ": " + self.name,
                        'dyman_order_id': self.process_id.order_id.id, 
                        'scheduled_date' : datetime.datetime.now(),
                        'picking_type_id': self.process_id.order_id.stock_picking_type_id.id
                        }      

                if self.final:
                    vals['location_id'] = self.process_id.order_id.wip_location_id.id
                else:
                    vals['location_dest_id'] = self.process_id.order_id.wip_location_id.id
                
                self.stock_picking_id = self.env['stock.picking'].create(vals)      

            vals = {
                    'name': _('New'),
                    'picking_id': self.stock_picking_id.id,
                    'product_id': material.material_id.id,
                    'product_uom_qty': material.quantity,
                    'location_id': self.stock_picking_id.location_id.id,
                    'location_dest_id': self.stock_picking_id.location_dest_id.id
                    }
            
            self.env['stock.move'].create(vals)                        
        
        if self.stock_picking_id:
            self.stock_picking_id.action_confirm()