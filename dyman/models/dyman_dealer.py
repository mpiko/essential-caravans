from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Dealer(models.Model):
    _name = "dyman.dealer"
    _description = "Dynamic product dealer"
    # A dealer is the owner of an order in the system

    _inherits = {'res.partner': 'partner_id'}
    
    name = fields.Char(string='Name', related="partner_id.name")
    partner_id = fields.Many2one("res.partner", string="Dealer", required=True, ondelete="restrict")
    user_access_ids = fields.One2many("dyman.dealer.user.access", "dealer_id", string="Users")
    available_product_line_ids = fields.One2many("dyman.product.line", string="Available product lines", compute="_load_available_product_lines")
    available_base_product_ids = fields.One2many("dyman.base.product", string="Available base products", compute="_load_available_base_products")

    @api.depends("partner_id")
    def _load_available_product_lines(self):
        for dealer in self:
            product_lines = []
            for product_line in self.env['dyman.product.line'].search([('active', '=', True)]):
                if product_line.available_to_dealers == 'most':
                    if dealer not in product_line.dealer_restriction_ids.dealer_id:
                        product_lines.append(product_line.id)
                elif product_line.available_to_dealers == 'selected':
                    if dealer in product_line.dealer_restriction_ids.dealer_id:
                        product_lines.append(product_line.id)
                else:
                    product_lines.append(product_line.id)

            if len(product_lines) == 0:
                product_lines = False

            dealer.available_product_line_ids = product_lines

    @api.depends("partner_id")
    def _load_available_base_products(self):
        for dealer in self:
            base_products = []
            for base_product in self.env['dyman.base.product'].search([('status', '=', 'active')]):
                available = False
                if base_product.product_line_id in dealer.available_product_line_ids:
                    available = True
                    for attribute in base_product.base_product_attribute_ids:
                        prodline_attrtype = self.env['dyman.prodline.attrtype'].search([('active', '=', True),('product_line_id', '=', base_product.product_line_id.id),('attribute_type_id', '=', attribute.attribute_type_id.id)])
                        if len(prodline_attrtype) != 1:
                            raise ValidationError(
                                "Expected to find a single active attribute of type " + attributeattribute_type_id + " on Product Line " + base_product.product_line_id + " but found " + str(len(prodline_attrtype)))

                        attribute_def = self.env['dyman.prodline.attrtype.attrval'].search([('prodline_attrtype_id', '=', prodline_attrtype[0].id), ('attribute_value_id', '=', attribute.attribute_value_id.id)])
                        if len(attribute_def) != 1:
                            raise ValidationError(
                                "Expected to find a single active attribute of type " + attributeattribute_type_id + " and value " + attribute.attribute_value_id + " on Product Line " + base_product.product_line_id + " but found " + str(len(attribute_def)))

                        if attribute_def.available_to_dealers == 'most':
                            if dealer in attribute_def.dealer_restriction_ids.dealer_id:
                                available = False
                                break
                        elif attribute_def.available_to_dealers == 'selected':
                            if dealer not in attribute_def.dealer_restriction_ids.dealer_id:
                                available = False
                                break

                if available:
                    base_products.append(base_product.id)

            if len(base_products) == 0:
                base_products = False

            dealer.available_base_product_ids = base_products

    def available_months(self):
        months = []
        open_months = self.env['dyman.build.month'].filtered(lambda r: r.status == "open")
        for month in open_months:
            allocations = self.env['dyman.production.allocation'].search([('dealer_id', '=', self.id), ('build_month_id', '=', month.id)])
            if len(allocations) == 0:
                allocation = 0
            elif len(allocations) > 1:
                raise ValidationError(self.name + " has more than 1 production allocation for " month.name)
            else:
                allocation = allocations[0].slots

            if len(self.env['dyman.order'].search([('dealer_id', '=', self.id), ('build_month_id', '=', month.id)])) < allocation:
                months.append(month)

        return months