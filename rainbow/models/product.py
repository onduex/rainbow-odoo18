# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.rainbow.tools.tools import convert_date
from odoo.addons.rainbow.tools.tools import convert_image

from odoo import _
from odoo import fields
from odoo import models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_vault_product = fields.Boolean(copy=False)
    vault_server_id = fields.Many2one(comodel_name='vault.server', string='Vault Server')
    vault_master_id = fields.Integer(string='Vault Master Id', copy=False)
    vault_internal_id = fields.Integer(string='Vault Id', copy=False)
    vault_last_update = fields.Datetime(string='Last update on Vault', copy=False)
    vault_revision = fields.Char(string='Vault Revision', copy=False)
    is_old_revision = fields.Boolean(string="Is old revision?", copy=False)
    vault_web_link = fields.Char(string="Vault Web link")
    vault_desktop_link = fields.Char(string="Vault Desktop link")

    _sql_constraints = [
        (
            "default_code_revision_uniq",
            "unique(default_code, vault_revision)",
            _("Both internal reference and revision must be unique!"),
        ),
    ]
