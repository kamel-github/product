
from odoo import api, fields, models

class Hrcompany(models.Model):
    # """
    # Employee contract based on the visa, work permits
    # allows to configure different Salary structure
    # """

    _inherit = 'res.company'
    _description = "Company"

    affiliation_CNSS = fields.Char(string="Affiliation CNSS")
