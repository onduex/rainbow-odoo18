# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models, _
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
