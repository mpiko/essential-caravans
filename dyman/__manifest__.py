{
    'name' : 'Dynamic Manufacturing',
    'author' : 'Lincoln Eddy',
    'version' : '18.0.1.0.1',
    'depends' : ['base', 'product', 'stock'],
    'data' : [
        'security/ir.model.access.csv',

        # views
        'views/dyman_product_line.xml',
        'views/dyman_attribute_type.xml',
        'views/dyman_attribute_value.xml',
        'views/dyman_base_product.xml',
        'views/dyman_base_material.xml',
        'views/dyman_base_material_update.xml',
        'views/dyman_component.xml',
        'views/dyman_operation.xml',
        'views/dyman_order.xml',
        'views/dyman_order_material.xml',
        'views/dyman_prodline_component_rule.xml',
        'views/dyman_prodline_filter.xml',
        'views/stock_picking.xml',
        'views/dyman_schedule_order.xml',
        'views/dyman_schedule.xml',
        'views/dyman_component_category.xml',
        'views/dyman_dealer.xml',
        'views/res_users.xml',
        'views/dyman_base_characteristic_update.xml',
        'views/dyman_menus.xml'
        ]
}
