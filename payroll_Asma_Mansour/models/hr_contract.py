# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrContract(models.Model):
    # """
    # Employee contract based on the visa, work permits
    # allows to configure different Salary structure
    # """

    _inherit = "hr.contract"
    _description = "Employee Contract"

    jour_de_repos_1 = fields.Selection(
        [
            ("Lundi", "Lundi"),
            ("Mardi", "Mardi"),
            ("Mercredi", "Mercredi"),
            ("Jeudi", "Jeudi"),
            ("Vendredi", "Vendredi"),
            ("Samedi", "Samedi"),
            ("Dimanche", "Dimanche"),
        ],
        string="Jour de repos 1", default='', tracking=True)

    jour_de_repos_2 = fields.Selection(
        [
            ("Lundi", "Lundi"),
            ("Mardi", "Mardi"),
            ("Mercredi", "Mercredi"),
            ("Jeudi", "Jeudi"),
            ("Vendredi", "Vendredi"),
            ("Samedi", "Samedi"),
            ("Dimanche", "Dimanche"),
        ],
        string="Jour de repos 2", default='', tracking=True)
    employee_id = fields.Many2one("hr.employee")
    salaire_de_base = fields.Char(string='Salaire de base selon la convention', related='employee_id.salaire_de_base')
    prime = fields.Monetary(string='Prime complémentaire', default=False, help="Employee's monthly prime.",tracking=True)
    net = fields.Monetary(string='Salaire Net', default=False, help="Employee's monthly net salary.",tracking=True)
    # type_id = fields.Selection(related='employee_id.categorie')