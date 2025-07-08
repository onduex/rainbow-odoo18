# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.rainbow.tools.tools import convert_date
from odoo.addons.rainbow.tools.tools import convert_image
from odoo.exceptions import ValidationError

from odoo import _
from odoo import api
from odoo import fields
from odoo import models


_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_vault_product = fields.Boolean(copy=False)
    vault_server_id = fields.Many2one(
        comodel_name='vault.server',
        string='Vault Server',
    )
    vault_master_id = fields.Integer(
        string='Vault Master Id',
        copy=False,
    )
    vault_internal_id = fields.Integer(
        string='Vault Id',
        copy=False,
    )
    vault_last_update = fields.Datetime(
        string='Last update on Vault',
        copy=False,
    )
    vault_revision = fields.Char(
        string='Vault Revision',
        copy=False,
    )
    is_old_revision = fields.Boolean(string="Is old revision?", copy=False)
    vault_web_link = fields.Char(
        string="Vault Web link",
        compute="_compute_vault_product_links",
    )
    vault_desktop_link = fields.Char(
        string="Vault Desktop link",
        compute="_compute_vault_product_links",
    )

    _sql_constraints = [
        (
            "default_code_revision_uniq",
            "unique(default_code, vault_revision)",
            _("Both internal reference and revision must be unique!"),
        ),
    ]

    def _compute_vault_product_links(self):
        ConfigParameter = self.env["ir.config_parameter"].sudo()
        for record in self:
            if record.is_vault_product:
                for app_type in "web desktop".split():
                    key = "vault_%s_link" % app_type
                    url = ConfigParameter.get_param(key, "")
                    if url:
                        value = (
                                app_type == "desktop" and record.default_code
                                or record.vault_master_id
                        )
                        record[key] = url.format(product=value)
            else:
                record.vault_web_link = ""
                record.vault_desktop_link = ""

    @api.returns('self')
    def _get_vault_products(self):
        dom = [
            ('is_vault_product', '=', True)
        ]
        return self.search(dom)

    @api.returns('self')
    def get_product_by_master_id(self, vault_master_id, server=None):
        dom = [('vault_master_id', '=', vault_master_id)]
        if server is not None:
            dom.append(('vault_server_id', '=', server.id))
        return self.search(dom, limit=1)

    @api.returns('self')
    def _get_product_by_master_and_internal_id(self, master_id, internal_id):
        dom = [
            ('vault_master_id', '=', master_id),
            ('vault_internal_id', '=', internal_id),
        ]
        return self.search(dom, limit=1)

    def sync_product(self):
        self.ensure_one()
        product = self
        update_products = product._sync_product()
        title = _("Product not synchronized")
        message = _("The product has the last version from Vault Server.")
        context = {}
        if update_products:
            title = _("Product synchronized correctly!")
            message = (_("Product synchronized."))
            context = update_products._context
        return self.env["vault.server"]._show_info_message(
            title=title,
            message=message,
            sticky=False,
            context=context,
        )

    @api.returns("self")
    def _sync_product(self):
        self.ensure_one()
        vault_server = self.vault_server_id
        if not vault_server:
            raise ValidationError(
                _("Please, its mandatory set a Vault Server to synchronize "
                  "products.")
            )
        return vault_server._sync_vault_products(products=self)

    def _is_vault_product_update(self, vault_internal_id):
        self.ensure_one()
        return self.vault_internal_id == vault_internal_id

    def _check_custom_properties(self):
        VaultProperty = self.env['vault.product.property']
        for product in self:
            product_values = dict()
            vault_server = product.vault_server_id
            method = (
                vault_server._get_property_values_by_product_and_property_id
            )
            properties = (
                VaultProperty._get_active_properties(vault_server)
            )
            vault_property_ids = properties.mapped("vault_internal_id")
            vault_property_values = method(product.vault_internal_id)
            property_values = [prop for prop in vault_property_values
                               if prop.PropDefId in vault_property_ids]
            for prop in properties:
                field = prop.product_field_id.name
                vault_property_values = [
                    vault_prop for vault_prop in property_values
                    if vault_prop.PropDefId == prop.vault_internal_id]
                if vault_property_values:
                    value = vault_property_values[0].Val
                    if prop.type.lower() in "date datetime".split():
                        value = convert_date(value)
                    elif prop.type.lower() == "image":
                        if value is not None:
                            value = convert_image(value)
                    if product[field] != value:
                        product_values[field] = value
            if product_values:
                product.write(product_values)
        return True

    @api.model
    def sync_vault_products(self):
        _logger.info('@Rainbow; Sync Vault products cron is running...')
        vault_server = self.env['vault.server'].search([], limit=1)
        if vault_server:
            vault_server._main_sync_vault_products()

    def _has_same_vault_revision(self, vault_revision):
        """Check if the vault version is the same"""
        self.ensure_one()
        return self.vault_revision == vault_revision

    def _has_same_vault_internal_id(self, vault_internal_id):
        """Check if the vault internal id is the same"""
        self.ensure_one()
        return self.vault_internal_id == vault_internal_id

    @api.model
    def _exists_product_by_master_and_revision(self, master_id, revision):
        dom = [
            ('vault_master_id', '=', master_id),
            ('vault_revision', '=', revision),
        ]
        return bool(self.search_count(dom))

    def name_get(self):
        res = super(ProductTemplate, self).name_get()
        res_ = []
        for item in res:
            product = self.browse(item[0])
            if product.is_vault_product:
                name = product._get_template_name_by_vault_revision()
                res_.append((product.id, name))
                continue
            res_.append(item)
        return res_

    def _get_template_name_by_vault_revision(self):
        self.ensure_one()
        return "[%s%s] %s" % (
            self.default_code,
            self.vault_revision and '-%s' % self.vault_revision or '',
            self.name,
        )

    def _set_old_revision(self):
        dom = [
            ('is_vault_product', '=', True),
            ('is_old_revision', '=', False),
        ]
        for product in self:
            _dom = list(dom)
            _dom.extend([
                ('id', '!=', product.id),
                ('default_code', '=', product.default_code),
            ])
            products = self.search(_dom)
            if products:
                products.write({'is_old_revision': True})

    @api.returns("self")
    def _get_product_not_linked_with_vault_server(self, default_code=None):
        product = self
        if default_code is not None:
            dom = [
                ("default_code", "=", default_code),
                ("is_vault_product", "=", False),
            ]
            product = self.search(dom, limit=1)
        return product

    def _update_values_by_old_revision(self, values: dict) -> None:
        self.ensure_one()
        vault_server = self.vault_server_id
        for field in vault_server.product_field_ids:
            value = self[field.name]
            if isinstance(value, models.Model):
                if field.ttype == "many2one":
                    value = value.id
                elif field.ttype in ("one2many", "many2many"):
                    value = [(6, 0, value.ids)]
                else:
                    _logger.info(
                        "@Rainbow; %s: Is not possible map the field %s in "
                        "the new revision.",
                        self.default_code,
                        field.name
                    )
                    continue
            values.update({field.name: value})

    def _get_duplicate_products(self, item, revision):
        domain = [
            ("vault_master_id", "=", item.get('MasterId', False)),
            ("vault_revision", "=", revision),
            ('default_code', '=', item.get('ItemNum', False))
        ]
        return self.search(domain, limit=1)

    def _update_product_data_by_revision(self, template):
        MrpBom = boms_archive = self.env['mrp.bom']
        MrpBomLine = bom_lines_to_update = self.env['mrp.bom.line']
        domain = [
            ("vault_master_id", "=", template.vault_master_id),
            ("vault_revision", "!=", template.vault_revision),
            ("vault_internal_id", ">", template.vault_internal_id),
        ]

        products_to_update = self.search(domain)
        for product_tmpl in products_to_update:
            product = fields.first(product_tmpl.product_variant_ids)
            domain = [("product_tmpl_id", "=", product_tmpl.id)]
            bom_line_domain = [("product_id", "=", product.id)]
            boms = MrpBom.search(domain)
            if boms:
                boms_archive |= boms

            bom_lines = MrpBomLine.search(bom_line_domain)
            if bom_lines:
                for line in bom_lines:
                    if line.bom_id.id in boms.ids:
                        continue
                    bom_lines_to_update |= line

        product = fields.first(template.product_variant_ids)
        if bom_lines_to_update and product:
            bom_lines_to_update.write({"product_id": product.id})

        if boms_archive:
            boms_archive.write({"active": False})

        if products_to_update:
            products_to_update.write({"active": False, "is_old_revision": True})

        update_values = {"is_old_revision": False}
        template.write(update_values)
        product.write(update_values)
        return True

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def sync_product(self):
        return self.product_tmpl_id.sync_product()

    def name_get(self):
        res = super(ProductProduct, self).name_get()
        res_ = []
        for item in res:
            product = self.browse(item[0])
            if product.is_vault_product:
                template = product.product_tmpl_id
                name = template._get_template_name_by_vault_revision()
                res_.append((product.id, name))
                continue
            res_.append(item)
        return res_
