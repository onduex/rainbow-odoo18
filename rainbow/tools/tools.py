# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import requests
import zeep

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


VAULT_SERVER_DATE_FORMAT = "%m/%d/%Y"
VAULT_SERVER_TIME_FORMAT = "%H:%M:%S"
VAULT_SERVER_DATETIME_FORMAT = "%s %s" % (
    VAULT_SERVER_DATE_FORMAT,
    VAULT_SERVER_TIME_FORMAT,
)


_CONNECTION_ERRORS = {
    "301": _("Error [301]\n\nWrong value for User name or User password."),
    "133": _("Error [133]\n\nWrong value for Database name."),
    "113": _("Error [113]\n\nConnection timed out. No route to host."),
    "110": _("Error [110]\n\nConnection timed out. Failed to establish a new "
             "connection."),
    "111": _("Error [111]\n\nConnection timed out. Failed to establish a new "
             "connection."),
    "system_error": _("System error\n\n%s"),
    "unknown": _("Unknown error\n\nPlease, contact with your system "
                 "administrator.\n\n%s")}


SEARCH_OPERATORS = {
    "in": 1,
    "not in": 2,
    "=": 3,
    "is null": 4,
    "is not null": 5,
    ">": 6,
    "after": 7,
    "<": 8,
    "is not": 10,
}


VAULT_TYPES_MAPPED = {
    "bool": ("boolean",),
    "datetime": ("datetime", "date",),
    "image": ("binary",),
    "numeric": ("float", "integer", "monetary",),
    "selection": ("char", "selection", "text",),
    "string": ("char", "selection", "text", "html",),
}


def convert_date(date):
    return fields.Datetime.to_datetime(fields.Datetime.to_string(date))


def convert_image(image):
    return fields.base64.b64encode(image)


def get_literal_by_records(total_records, literal):
    return literal if total_records == 1 else f"{literal}s"
