from odoo import _, api, fields, models

class ContractHistory(models.Model):
    _inherit = 'hr.contract.history'

    net = fields.Monetary(string='Salaire Net', related='contract_id.net', readonly=True)
    contract_type_id = fields.Many2one(string='Contract Type', related='contract_id.contract_type_id', readonly=True)