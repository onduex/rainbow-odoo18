# -*- coding: utf-8 -*-

import logging

from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class ResEndpoint(models.Model):
    _name = 'res.endpoint'
    _description = "Endpoint Configuration"
    _order = 'id'

    name = fields.Char(string='Router', required=True, help='Router name')
    full_name = fields.Char(string='Full name', compute='_compute_full_name', store=True,
                            help='Full name of the endpoint')
    vault_server_id = fields.Many2one(comodel_name='vault.server', string='Vault server', required=False)
    method = fields.Selection(
        string='Method',
        selection=[('post', 'POST'),
                   ('get', 'GET'),
                   ('put', 'PUT'),
                   ('delete', 'DELETE')],
        required=False, )


    @api.depends('name', 'vault_server_id')
    def _compute_full_name(self):
        for endpoint in self:
            prefix = ''
            if endpoint.vault_server_id:
                prefix = endpoint.vault_server_id.name

            if prefix and endpoint.name:
                endpoint.full_name = f"{prefix}{endpoint.name}"
            else:
                endpoint.full_name = endpoint.name or ''
