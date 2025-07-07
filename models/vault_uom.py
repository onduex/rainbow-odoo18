# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class VaultUom(models.Model):
    _name = 'vault.uom'
    _description = 'Vault UoM'
    _order = 'vault_internal_id'

    name = fields.Char(string='Name', copy=False)
    vault_internal_id = fields.Integer(string='Vault Id',)
    vault_sys_name = fields.Char(string='Vault Sys Name')
    uom_id = fields.Many2one(comodel_name='uom.uom', string='Odoo UoM')
    vault_server_id = fields.Many2one(
        comodel_name='vault.server', string='Vault Server')
    abbreviation = fields.Char(string='Abbreviation')
    conversion = fields.Float(string='Conversion')

    @api.returns('self')
    def get_vault_uom_by_id(self, vault_internal_id, server, for_product=False):
        dom = [
            ('vault_internal_id', '=', vault_internal_id),
            ('vault_server_id', '=', server.id)
        ]
        vault_uom = self.search(dom, limit=1)
        if for_product and not vault_uom.uom_id:
            raise ValidationError(
                _('No one Odoo UoM mapped with the [%s] Vault UoM!\nPlease, '
                  'make sure to map all Vault UoM before to import new '
                  'products.') % vault_uom.name or vault_uom.vault_internal_id)
        return vault_uom

    def _mapper_vault_uom(self):
        """
        Method to mapper Vault UoM imported from Vault server with the Odoo's
        UoM.
        :return: True
        """
        Uom = self.env['uom.uom']
        for vault_uom in self:
            dom = [
                ('name', '=', vault_uom.abbreviation)
            ]
            uom = Uom.search(dom, limit=1)
            if uom:
                vault_uom.write({'uom_id': uom.id})
        return True
