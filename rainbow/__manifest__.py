# -*- coding: utf-8 -*-
{
    'name': "Rainbow Link",
    'summary': """
        Create products from Autodesk Vault Items
        """,
    'description': """
        Create products from Autodesk Vault Items
        """,
    'author': "Onduex sl",
    'website': "https://www.onduex.com",
    'category': 'Inventory',
    'version': '18.0.0.1',
    'depends': [
        'base',
        'mrp',
        'stock',
    ],
    'external_dependencies': {
        'python': ['zeep'],
    },
    'data': [
        # DATA
        # 'data/ir_config_parameter_data.xml',
        # 'data/ir_cron_data.xml',
        # 'data/res_groups_data.xml',
        # 'data/vault_server_data.xml',
        # SECURITY
        'security/ir.model.access.csv',
        # VIEWS
        'views/product_views.xml',
        'views/vault_server_views.xml',
        'views/rainbow_server_views.xml'
        # 'views/vault_life_cycle_views.xml',
        # 'views/vault_service_views.xml',
        # 'views/vault_category_views.xml',
        # 'views/vault_uom_views.xml',
        # 'views/res_config_settings_views.xml',
    ],

    'images': ['images/main_screenshot.png'],
    'license': 'Other proprietary',
    'installable': True,
    'application': True,
    'post_init_hook': '_activate_group_uom',
}
