# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.queue_job.job import job

except ImportError:
    _logger.debug("Can not `import queue_job`.")
    import functools


class RainbowServer(models.Model):
    _name = 'rainbow.server'
    _description = "Rainbow Server"
    _order = 'id'

    name = fields.Char(
        string='Server host', required=True,
        help='Autodesk Vault server host name or IP')
    endpoint_password = fields.Char(
        string='Endpoint password', required=True,
        help='Rainbow server endpoint password')

    @api.model_create_multi
    def create(self, vals):
        if self.search_count([]) > 0:
            raise ValidationError(_("Solo puede existir un registro de este modelo."))
        return super().create(vals)