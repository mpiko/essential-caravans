from odoo import api, fields, models

class ComponentProcessOperation(models.Model):
    _name = "dyman.component.process.operation"
    _description = "Dynamic product component process operation"
    # The assignment of a component to a Process Operation, being the manufacturing operation in which the material for the component is consumed into the build.

    name = fields.Char(string="Name", related="component_id.name")
    component_id = fields.Many2one("dyman.component", string="Component", domain="[('id', 'in', valid_component_ids)]", ondelete="cascade")
    process_operation_id = fields.Many2one("dyman.process.operation", string="Operation", ondelete="restrict")
    valid_component_ids = fields.One2many("dyman.component", string="Valid components", compute="_load_valid_components")

    @api.depends("process_operation_id")
    def _load_valid_components(self):
        for record in self:
            record.valid_component_ids = record._get_valid_components()

    def _get_valid_components(self):
        component_id_list = []
        for component in self.process_operation_id.process_id.product_line_id.prodline_component_ids:
            component_id_list.append(component.component_id.id)

        return component_id_list