# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import requests

from odoo import api, models, fields
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

    app_code = fields.Char(string='appCode', required=True, default='RBWL-V2')
    type = fields.Selection(
        string='Type',
        selection=[('vault', 'Vault'), ('rainbow', 'Rainbow')],
        required=False, default='vault',)
    name = fields.Char(
        string='Name', required=True,
        default='https://gateway.autodesk.com/AutodeskDM/Services/api/vault/v2'
    )
    user_name = fields.Char(
        string='userName', required=False, help='Autodesk Vault user name')
    user_password = fields.Char(
        string='password', required=True,
        help='Autodesk Vault user password')
    knowledge_vault = fields.Char(
        string='vault', required=False, help='Autodesk Vault DB name')
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

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if not record.name:
                record.name = f"00{record.id}"
        return records

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

            # Accede al diccionario 'vaultInformation' y luego a la clave 'id'
            vault_info = data.get('vaultInformation')
            if vault_info:
                self.vault_id = vault_info.get('id')

            # Accede al diccionario 'userInformation' y luego a la clave 'id'
            user_info = data.get('userInformation')
            if user_info:
                self.vault_user_id = user_info.get('id')

            # Define la acción de recarga que se ejecutará después de la notificación.
            reload_action = {'type': 'ir.actions.client', 'tag': 'reload'}

            if access_token:
                self.token = access_token
                # Devuelve una notificación de éxito que, al cerrarse, recargará la vista.
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Conexión Exitosa'),
                        'message': _('Token recibido y guardado.'),
                        'type': 'success',
                        'sticky': False,
                        'next': reload_action,
                    }
                }
            else:
                # Devuelve una notificación de advertencia que, al cerrarse, recargará la vista.
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Conexión Exitosa'),
                        'message': _('La conexión se realizó, pero no se recibió un token.'),
                        'type': 'warning',
                        'sticky': True,  # La dejamos fija para que el usuario la vea bien.
                        'next': reload_action,
                    }
                }
        except Exception as e:
            raise ValidationError(_("Error al conectar con Vault (POST): %s") % str(e))
