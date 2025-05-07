from odoo import api, fields, models

class ProductLineComponent(models.Model):
    _name = "dyman.prodline.component"
    _description = "Dynamic product line component"
    # The assignment of a component to a product line - via the component category

    name = fields.Char(string='Name', related="component_id.name")
    product_component_category_id = fields.Many2one("dyman.prodline.component.category", string="Component category", required=True, ondelete="restrict")
    component_id = fields.Many2one("dyman.component", string="Component", ondelete="restrict")
    include_on_spec_report = fields.Boolean(string="Include on spec sheet", default=True)
    operation_id = fields.Many2one("dyman.operation", string="Operation", domain="[('id', 'in', valid_operation_ids)]", ondelete="restrict")
    valid_operation_ids = fields.One2many("dyman.operation",string="Valid operations",compute="_load_valid_operations")
    alert_always_operation_ids = fields.Many2many("dyman.operation", "prodline_component_operation_alert_always", "prodline_component_id", "operation_id", string="Operations to alert always", domain="[('id', 'in', valid_operation_ids)]")
    alert_onchange_operation_ids = fields.Many2many("dyman.operation", "prodline_component_operation_alert_onchange", "prodline_component_id", "operation_id", string="Operations to alert on change", domain="[('id', 'in', valid_operation_ids)]")
    material_ids = fields.One2many("dyman.prodline.component.material", "prodline_component_id", string="Materials (parts)")

    @api.depends("product_component_category_id")
    def _load_valid_operations(self):
        for record in self:
            operation_ids = self.env['dyman.prodline.operation'].search([("product_line_id", "=", record.product_component_category_id.product_line_id.id)]).mapped("operation_id.id")
            if len(operation_ids) == 0:
                operation_ids = False

            record.valid_operation_ids = operation_ids