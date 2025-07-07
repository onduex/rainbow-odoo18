# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models, _
from odoo.addons.rainbow.controllers.main import service_client
from odoo.addons.rainbow.controllers.main import vault_log
from odoo.addons.rainbow.tools.tools import SEARCH_OPERATORS
from odoo.addons.rainbow.tools.tools import VAULT_SERVER_DATETIME_FORMAT
from odoo.addons.rainbow.tools.tools import convert_date
from odoo.addons.rainbow.tools.tools import get_literal_by_records
from odoo.addons.rainbow.tools.tools import serialize_zeep_object_list
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.queue_job.job import job

except ImportError:
    _logger.debug("Can not `import queue_job`.")
    import functools


class VaultServer(models.Model):
    _name = 'vault.server'
    _description = "Vault Server"
    _order = 'id'

    name = fields.Char(string='Server name', required=True)
    host_name = fields.Char(
        string='Server host', required=True,
        help='Autodesk Vault server host name or IP')
    port = fields.Char(string='Port')
    user_name = fields.Char(
        string='User name', required=True, help='Autodesk Vault user name')
    user_password = fields.Char(
        string='User password', required=True,
        help='Autodesk Vault user password')
    knowledge_vault = fields.Char(
        string='Database name', required=True, help='Autodesk Vault DB name')
    token = fields.Char(
        string='Token', help='Security Token of the current connection')
    vault_user_id = fields.Integer(
        string='User id', help='Vault user Id of the current connection')
    total_vault_products = fields.Integer(
        string='Products imported', compute='_compute_total_vault_products')
    vault_product_property_ids = fields.One2many(
        comodel_name='vault.product.property', inverse_name='vault_server_id',
        string='Vault product properties')
    vault_custom_revision = fields.Many2one(
        comodel_name='vault.product.property',
        string='Vault revision',
        help='Set the Vault property used to compare revisions on update process.',
        domain="[('odoo_field_ids.ttype', 'in', ['char', 'float'])]",
    )
    has_properties = fields.Boolean(compute='_compute_has_properties')
    product_field_ids = fields.Many2many(
        comodel_name='ir.model.fields',
        string='Product fields',
        domain="[('model_id.model', '=', 'product.template')]",
    )
    request_from = fields.Datetime(
        string='Vault update date from',
        help='Vault update date from to request to Vault server. You can set any hour to subtract in the following field.',
        copy=False,
    )
    hours_to_subtract = fields.Integer(string='Hours to subtract')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        help="Set the Company over which to create the products",
    )


class VaultServerLog(models.Model):
    _name = 'vault.server.log'
    _description = "Vault Server Logs"
    _order = 'id desc'

    user_id = fields.Many2one(comodel_name='res.users', string='User')
    action = fields.Char(string='Action')
    vault_user_id = fields.Integer(string='Vault user')
    vault_server = fields.Char(string='Vault server')
    vault_host = fields.Char(string='Server host')
    knowledge_vault = fields.Char(string='Vault database')
