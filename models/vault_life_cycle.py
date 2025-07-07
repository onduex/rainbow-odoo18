# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api
from odoo.tools.translate import _


class VaultLifeCycle(models.Model):
    _name = 'vault.life.cycle'
    _description = 'Vault Life Cycle'
    _order = 'vault_internal_id'

    def _compute_total_states(self):
        for life_cycle in self:
            life_cycle.total_states = len(life_cycle.life_cycle_state_ids)

    name = fields.Char(string='Name', copy=False)
    description = fields.Char(string='Description')
    vault_internal_id = fields.Integer(string='Vault Id')
    sys_name = fields.Char(string='Vault Sys Name')
    vault_server_id = fields.Many2one(
        comodel_name='vault.server', string='Vault Server')
    life_cycle_state_ids = fields.One2many(
        comodel_name='vault.life.cycle.state', inverse_name='life_cycle_id',
        string='States')
    total_states = fields.Integer(
        string='Total states', compute='_compute_total_states')

    @api.returns('self')
    def get_vault_life_cycle_by_id(self, vault_internal_id, server):
        dom = [
            ('vault_internal_id', '=', vault_internal_id),
            ('vault_server_id', '=', server.id)
        ]
        life_cycle = self.search(dom, limit=1)
        return life_cycle

    _sql_constraints = [
        (
            'uniq_vault_internal_id',
            'unique(vault_internal_id)',
            _('vault_internal_id must be unique across the database!')
        )]


class VaultLifeCycleState(models.Model):
    _name = 'vault.life.cycle.state'
    _description = 'Vault Life Cycle State'
    _order = 'vault_internal_id'

    name = fields.Char(string='Name', copy=False)
    description = fields.Char(string='Description')
    vault_internal_id = fields.Integer(string='Vault Id')
    is_release = fields.Boolean(string='Is release?')
    is_obsolete = fields.Boolean(string='Is obsolete?')
    life_cycle_id = fields.Many2one(
        comodel_name='vault.life.cycle' ,string='Life Cycle')
    use_to_import = fields.Boolean(
        string='Use to import Products',
        help='Check if you want import products from Vault Server with this '
             'state.')

    @api.returns('self')
    def get_vault_life_cycle_state_by_id(self, vault_internal_id):
        dom = [('vault_internal_id', '=', vault_internal_id)]
        life_cycle_state = self.search(dom, limit=1)
        return life_cycle_state

    @api.returns('self')
    def _get_vault_cycle_states_to_import_items(self, vault_server):
        dom = [
            ('life_cycle_id.vault_server_id', '=', vault_server.id),
            ('use_to_import', '=', True),
        ]
        return self.search(dom)

    _sql_constraints = [
        (
            'uniq_vault_internal_id',
            'unique(vault_internal_id)',
            _('vault_internal_id must be unique across the database!')
        )]
