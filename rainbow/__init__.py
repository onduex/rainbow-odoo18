# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# from . import controllers
from . import models
# from . import tools
from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def _activate_group_uom(env):
    _logger.info('@Rainbow; Activate UoM on system.')
    env['res.config.settings'].create({'group_uom': True})
