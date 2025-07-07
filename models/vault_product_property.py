# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.addons.rainbow.tools.tools import VAULT_TYPES_MAPPED

_logger = logging.getLogger(__name__)


class VaultProductProperty(models.Model):
    _name = 'vault.product.property'
    _description = 'Vault Product Properties'
    _order = 'vault_internal_id'

    name = fields.Char(string='Name', copy=False)
    vault_name = fields.Char(string='Vault Name', copy=False)
    vault_internal_id = fields.Integer(string='Vault Id')
    type = fields.Char(string='Type')
    odoo_field_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        string='Odoo fields',
        compute='_compute_odoo_field_ids',
        store=True,
    )
    product_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Product field')
    vault_server_id = fields.Many2one(
        comodel_name='vault.server', string='Vault Server')

    @api.depends('type')
    def _compute_odoo_field_ids(self):
        Fields = self.env["ir.model.fields"]
        for property in self:
            property_type = property.type.lower()
            odoo_field_types = VAULT_TYPES_MAPPED.get(property_type)
            domain = [
                ("model_id.model", "=", "product.template"),
                ("ttype", "in", odoo_field_types),
            ]
            property.odoo_field_ids = Fields.search(domain)

    @api.returns('self')
    def get_property_by_name(self, property_name):
        dom = [
            ('vault_name', '=', property_name)
        ]
        product_property = self.search(dom, limit=1)
        if not product_property:
            raise ValidationError(
                _('No one property named [%s]!') % property_name
            )
        return product_property

    @api.returns('self')
    def get_property_by_id(self, vault_internal_id, server):
        dom = [
            ('vault_internal_id', '=', vault_internal_id),
            ('vault_server_id', '=', server.id)
        ]
        vault_properties = self.search(dom)
        return vault_properties

    @api.returns('self')
    def _get_active_properties(self, server):
        """
        Get properties mapped with product Odoo fields.
        :return:
        """
        dom = [
            ('product_field_id', '!=', False),
            ('vault_server_id', '=', server.id)
        ]
        return self.search(dom)
