# -*- coding: utf-8 -*-
import logging

from odoo import fields

_logger = logging.getLogger(__name__)

VAULT_SERVER_DATE_FORMAT = "%m/%d/%Y"
VAULT_SERVER_TIME_FORMAT = "%H:%M:%S"
VAULT_SERVER_DATETIME_FORMAT = "%s %s" % (VAULT_SERVER_DATE_FORMAT, VAULT_SERVER_TIME_FORMAT)

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
