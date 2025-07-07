# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class VaultCategory(models.Model):
    _name = 'vault.category'
    _description = 'Vault Category'
    _order = 'vault_internal_id'

    name = fields.Char(string='Name', copy=False)
    vault_internal_id = fields.Integer(string='Vault Id')
    vault_sys_name = fields.Char(string='Vault Sys Name')
    product_categ_id = fields.Many2one(
        comodel_name='product.category',
        string='Odoo category',
    )
    vault_server_id = fields.Many2one(
        comodel_name='vault.server',
        string='Vault Server',
    )
    description = fields.Char(string='Description')
    route_ids = fields.Many2many(
        comodel_name="stock.route",
        string="Route",
        readonly=False,
        ondelete="cascade",
        domain=[('product_selectable', '=', True)]
    )
    type = fields.Selection([
        ('product', 'Storable Product'),
        ('consu', 'Consumable'),
        ('service', 'Service')], string='Product Type', default='product', required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
    no_update_categ_id = fields.Boolean(
        string="Don't update category",
        help="Mark it if you don't want to update the Odoo category on the "
             "update process.",
    )
    no_update_route_ids = fields.Boolean(
        string="Don't update routes",
        help="Mark it if you don't want to update the Odoo routes on the "
             "update process.",
    )
    no_update_type = fields.Boolean(
        string="Don't update type",
        help="Mark it if you don't want to update the Odoo type on the "
             "update process.",
    )

    @api.returns('self')
    def get_vault_category_by_id(self, vault_internal_id, server):
        dom = [
            ('vault_internal_id', '=', vault_internal_id),
            ('vault_server_id', '=', server.id),
        ]
        vault_category = self.search(dom, limit=1)
        return vault_category

    def _mapper_vault_categories(self):
        """
        Method to mapper Vault categories imported from Vault server with the
        Odoo's categories.
        :return: True
        """
        ConfigParameter = self.env['ir.config_parameter']
        ProductCategory = parent_category = self.env['product.category']
        create_categories = eval(ConfigParameter.get_param(
            'vault.create.categories', default='False'))
        if create_categories:
            parent_categ_id = eval(ConfigParameter.get_param(
                'vault.parent.category', default=[]))
            parent_category = ProductCategory.browse(parent_categ_id)
        for vault_category in self:
            domain = [('name', 'in', (
                vault_category.name, vault_category.description))]
            category = ProductCategory.search(domain, limit=1)
            if category:
                vault_category.write({'product_categ_id': category.id})
                continue
            if create_categories:
                new_category = ProductCategory.create({
                    'name': vault_category.name,
                    'parent_id': parent_category.id})
                vault_category.write({'product_categ_id': new_category.id})
        return True

    @api.returns('stock.route')
    def _get_routes(self):
        return self.route_ids

    def _set_extra_values(self, values, create=False):
        self.ensure_one()
        field_ref = "no_update_%s"
        for field in ("categ_id", "route_ids", "type"):
            if create or not self[field_ref % field]:
                value = (
                    self.product_categ_id.id if "categ" in field
                    else self.type if "type" in field
                    else [(6, 0, self._get_routes().ids)]
                )
                values[field] = value
