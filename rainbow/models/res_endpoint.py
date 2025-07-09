# -*- coding: utf-8 -*-

import logging

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ResEndpoint(models.Model):
    _name = 'res.endpoint'
    _description = "Endpoint Configuration"
    _order = 'id'

    name = fields.Char(string='Router', required=True, help='Router name')
    vault_server_id = fields.Many2one(comodel_name='vault.server', string='Vault server', required=False)
    rainbow_server_id = fields.Many2one(comodel_name='rainbow.server', string='Rainbow server', required=False)
