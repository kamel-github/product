# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

#
class Hraccount(models.Model):
    # """
    # Employee contract based on the visa, work permits
    # allows to configure different Salary structure
    # """

    _inherit = 'account.account'
    _description = "Account Pay Slip"

    # account_debit = fields.Many2one('om_hr_payroll_account', 'Debit Account', domain=[('deprecated', '=', False)])
    # account_credit = fields.Many2one('om_hr_payroll_account', 'Credit Account', domain=[('deprecated', '=', False)])

    
