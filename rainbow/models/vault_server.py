# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import requests

from odoo import models, fields
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
    app_code = fields.Char(string='appCode', required=True, default='RBWL-V2')
    host_name = fields.Char(
        string='Server host', required=True,
        help='Autodesk Vault server host name or IP')
    user_name = fields.Char(
        string='userName', required=True, help='Autodesk Vault user name')
    user_password = fields.Char(
        string='password', required=True,
        help='Autodesk Vault user password')
    knowledge_vault = fields.Char(
        string='vault', required=True, help='Autodesk Vault DB name')
    token = fields.Char(
        string='accesToken', help='Security Token of the current connection')
    vault_user_id = fields.Integer(
        string='User id', help='Vault user Id of the current connection')
    vault_id = fields.Integer(
        string='Vault id', help='Vault Id')
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

    def test_connection(self):
        self.ensure_one()
        url = self.host_name + "/auth/login"
        login_data = {
            "input": {
                "vault": self.knowledge_vault,
                "userName": self.user_name,
                "password": self.user_password,
                "appCode": self.app_code or "RBLv2"
            }
        }
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, json=login_data, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            access_token = data.get("accessToken") or data.get("token")
            if access_token:
                self.token = access_token
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Conexión POST exitosa'),
                    'message': _('Respuesta recibida y procesada.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            raise ValidationError(_("Error al conectar con Vault (POST): %s") % str(e))
