from odoo import api, fields, models
from odoo.exceptions import ValidationError
import datetime

class BaseMaterialUpdate(models.Model):
    _name = "dyman.base.material.update"
    _description = "Base product material update rule"
    # A definition for a rule to update Base Material records

    product_line_id = fields.Many2one("dyman.product.line", string="Product line", ondelete='cascade')
    component_id = fields.Many2one("dyman.component", string="Component", domain="[('id', 'in', valid_component_ids)]")
    valid_component_ids = fields.One2many("dyman.component", string="Valid components", compute="_load_valid_components")
    material_id = fields.Many2one("product.product", string="Material")
    quantity = fields.Float(string="Quantity", default=1)
    include_where = fields.Char(string="Include where")
    only_where = fields.Char(string="Only where")
    not_where = fields.Char(string="Not where")
    base_material_update_log_ids = fields.One2many("dyman.base.material.update.log", "base_material_update_id", string="Updates")
    last_applied = fields.Datetime(string="Last applied")

    @api.depends("product_line_id")
    def _load_valid_components(self):
        for record in self:
            record.valid_component_ids = record._get_valid_components()

    def _get_valid_components(self):
        component_id_list = []
        for component in self.product_line_id.prodline_component_category_ids.component_ids:
            component_id_list.append(component.component_id.id)

        return component_id_list
    
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
                'base_material_update_id': self.id,
                'applied_time': timestamp
                }
        self.env['dyman.base.material.update.log'].create(vals)

        self.last_applied = timestamp

        return {'return':True, 'type': 'ir.actions.act_window_close'}
                
    def _apply_to(self, base_prod):

        existing_materials = self.env['dyman.base.material'].search([('base_product_id','=',base_prod.id), ('component_id','=',self.component_id.id)])

        for existing_material in existing_materials:
            existing_material.unlink()

        if self.material_id and self.quantity > 0:

            vals = {
                    'base_product_id': base_prod.id,
                    'component_id': self.component_id.id,
                    'material_id': self.material_id.id,
                    'quantity': self.quantity,
                    }
            self.env['dyman.base.material'].create(vals)

