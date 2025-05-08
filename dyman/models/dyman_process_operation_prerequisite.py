from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ProcessOperationPrerequisite(models.Model):
    _name = "dyman.process.operation.prerequisite"
    _description = "Dynamic manufacturing prerequisite"
    # The assignment of a pre-requisite operation to a process operation

    name = fields.Char(string = "name", related="prerequisite_process_operation_id.name")
    process_operation_id = fields.Many2one("dyman.process.operation", string="Operation", required=True, ondelete="cascade")
    prerequisite_process_operation_id = fields.Many2one("dyman.process.operation", string="Pre-requisite", domain="[('id', 'in', valid_prerequisite_process_operation_ids)]", required=True, ondelete="restrict")
    valid_prerequisite_process_operation_ids = fields.One2many(string="Valid pre-requisites", related="process_operation_id.process_id.process_operation_ids", store=False)

    @api.onchange('process_operation_id', "prerequisite_process_operation_id")
    def _check_for_circular_reference(self):
        if self.process_operation_id.check_circular_reference(self.process_operation_id._origin):
            raise ValidationError("Applying this pre-requisite would create a circular reference")