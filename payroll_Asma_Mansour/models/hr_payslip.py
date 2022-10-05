# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo import api, fields, models, _
from odoo.tools import float_round, date_utils, convert_file, html2plaintext

class HrPayslip(models.Model):
    # """
    # Employee contract based on the visa, work permits
    # allows to configure different Salary structure
    # """

    _inherit = "hr.payslip"
    _description = "Employee Pay Slip"

    working_days = fields.Integer(string='Working days', compute='_compute_working_days', inverse="_set_compte", readonly= False, store=True,)
    jour_de_repos_1 = fields.Selection('hr', related='contract_id.jour_de_repos_1')
    jour_de_repos_2 = fields.Selection('hr', related='contract_id.jour_de_repos_2')
    sum_worked_hours = fields.Float(compute='_compute_worked_hours', store=True,
                                    help='Total hours of attendance and time off (paid or not)')
    month_date_from = fields.Char(string="Période de paie", compute="_compute_month_and_year_date_from")
    year_date_from = fields.Char(string="Year Date From", compute="_compute_month_and_year_date_from")
    month_date_to = fields.Char(string="Mois de paie", compute="_compute_month_and_year_date_to")
    year_date_to = fields.Char(string="Year Date To", compute="_compute_month_and_year_date_to")

    @api.depends('date_from')
    def _compute_month_and_year_date_from(self):
        for rec in self:
            date = rec.date_from
            b = str(date).split("-")[1]
            rec.year_date_from = str(date).split("-")[0]
            if b == "01":
                rec.month_date_from = "Janvier "
            elif b == "02":
                rec.month_date_from = "Février"
            elif b == "03":
                rec.month_date_from = "Mars"
            elif b == "04":
                rec.month_date_from = "Avril "
            elif b == "05":
                rec.month_date_from = "Mai"
            elif b == "06":
                rec.month_date_from = "Juin"
            elif b == "07":
                rec.month_date_from = "Juillet"
            elif b == "08":
                rec.month_date_from = "Août"
            elif b == "09":
                rec.month_date_from = "Septembre"
            elif b == "10":
                rec.month_date_from = "Octobre"
            elif b == "11":
                rec.month_date_from = "Novembre"
            elif b == "12":
                rec.month_date_from = "Décembre"

    @api.depends('date_to')
    def _compute_month_and_year_date_to(self):
        for rec in self:
            date = rec.date_to
            b = str(date).split("-")[1]
            rec.year_date_to = str(date).split("-")[0]
            if b == "01":
                rec.month_date_to = "Janvier "
            elif b == "02":
                rec.month_date_to = "Février"
            elif b == "03":
                rec.month_date_to = "Mars"
            elif b == "04":
                rec.month_date_to = "Avril "
            elif b == "05":
                rec.month_date_to = "Mai"
            elif b == "06":
                rec.month_date_to = "Juin"
            elif b == "07":
                rec.month_date_to = "Juillet"
            elif b == "08":
                rec.month_date_to = "Août"
            elif b == "09":
                rec.month_date_to = "Septembre"
            elif b == "10":
                rec.month_date_to = "Octobre"
            elif b == "11":
                rec.month_date_to = "Novembre"
            elif b == "12":
                rec.month_date_to = "Décembre"





    @api.depends('worked_days_line_ids.number_of_hours')
    def _compute_worked_hours(self):
        for payslip in self:
            payslip.sum_worked_hours = float(sum([line.number_of_hours for line in payslip.worked_days_line_ids]))

    @api.depends('jour_de_repos_1', 'jour_de_repos_2', 'date_to', 'date_from')
    def _compute_working_days(self):
        for record in self:
            # if record.jour_de_repos_1 == "Lundi":
            #     record.working_days = 20
            # else:
            #     record.working_days = 26
            y = 0
            f = (record.date_to - record.date_from).days
            a = str(record.date_from)[:4]
            b = str(record.date_from)[5:7]
            # b1 = str(record.date_to)[5:7]
            c = str(record.date_from)[-2:]
            if record.jour_de_repos_1 == "Lundi":
                k1 = 0
            elif record.jour_de_repos_1 == "Mardi":
                k1 = 1
            elif record.jour_de_repos_1 == "Mercredi":
                k1 = 2
            elif record.jour_de_repos_1 == "Jeudi":
                k1 = 3
            elif record.jour_de_repos_1 == "Vendredi":
                k1 = 4
            elif record.jour_de_repos_1 == "Samedi":
                k1 = 5
            else:
                k1 = 6
            if record.jour_de_repos_2 == "Lundi":
                q1 = 0
            elif record.jour_de_repos_2 == "Mardi":
                q1 = 1
            elif record.jour_de_repos_2 == "Mercredi":
                q1 = 2
            elif record.jour_de_repos_2 == "Jeudi":
                q1 = 3
            elif record.jour_de_repos_2 == "Vendredi":
                q1 = 4
            elif record.jour_de_repos_2 == "Samedi":
                q1 = 5
            elif record.jour_de_repos_2 == "Dimanche":
                q1 = 6
            else:
                q1 = ""

            for i in range(0, f + 1):
                x = date(int(a), int(b), int(c)) + timedelta(days=i)
                print(x)
                try:
                    if x.weekday() != int(k1) and x.weekday() != int(q1):
                        y += 1
                        record.working_days = y
                except:
                    if x.weekday() != int(k1):
                        y += 1
                        record.working_days = y

    def _set_compte(self):
        pass



    def _get_localdict(self):
        self.ensure_one()
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}

        employee = self.employee_id
        contract = self.contract_id

        localdict = {
            **self._get_base_local_dict(),
            **{
                'categories': BrowsableObject(employee.id, {}, self.env),
                'rules': BrowsableObject(employee.id, {}, self.env),
                'payslip': Payslips(employee.id, self, self.env),
                'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
                'inputs': InputLine(employee.id, inputs_dict, self.env),
                'employee': employee,
                'contract': contract,
                'result_rules': ResultRules(employee.id, {}, self.env)
            }
        }
        return localdict

    def _get_payslip_lines(self):
        self.ensure_one()

        localdict = self.env.context.get('force_payslip_localdict', None)
        if localdict is None:
            localdict = self._get_localdict()

        rules_dict = localdict['rules'].dict
        result_rules_dict = localdict['result_rules'].dict

        blacklisted_rule_ids = self.env.context.get('prevent_payslip_computation_line_ids', [])

        result = {}

        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            if rule.id in blacklisted_rule_ids:
                continue
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100,
                'result_name': False,
            })
            if rule._satisfy_condition(localdict):
                amount, qty, rate = rule._compute_rule(localdict)
                #check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                result_rules_dict[rule.code] = {'total': tot_rule, 'amount': amount, 'quantity': qty}
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = rule.category_id._sum_salary_rule_category(localdict, tot_rule - previous_amount)
                # Retrieve the line name in the employee's lang
                employee_lang = self.employee_id.sudo().address_home_id.lang
                # This actually has an impact, don't remove this line
                context = {'lang': employee_lang}
                if localdict['result_name']:
                    rule_name = localdict['result_name']
                elif rule.code in ['BASIC', 'GROSS', 'NET', 'DEDUCTION', 'REIMBURSEMENT']:  # Generated by default_get (no xmlid)
                    if rule.code == 'BASIC':  # Note: Crappy way to code this, but _(foo) is forbidden. Make a method in master to be overridden, using the structure code
                        if rule.name == "Double Holiday Pay":
                            rule_name = _("Double Holiday Pay")
                        if rule.struct_id.name == "CP200: Employees 13th Month":
                            rule_name = _("Prorated end-of-year bonus")
                        else:
                            rule_name = _('Salaire de base')
                    elif rule.code == "GROSS":
                        rule_name = _('Salaire Brut')
                    elif rule.code == "DEDUCTION":
                        rule_name = _('Deduction')
                    elif rule.code == "REIMBURSEMENT":
                        rule_name = _('Reimbursement')
                    elif rule.code == 'NET':
                        rule_name = _('Salaire Net')
                else:
                    rule_name = rule.with_context(lang=employee_lang).name
                # create/overwrite the rule in the temporary results
                result[rule.code] = {
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'name': rule_name,
                    'note': html2plaintext(rule.note),
                    'salary_rule_id': rule.id,
                    'contract_id': localdict['contract'].id,
                    'employee_id': localdict['employee'].id,
                    'amount': amount,
                    'quantity': qty,
                    'rate': rate,
                    'slip_id': self.id,
                }
        return result.values()

class HrPayslip(models.Model):

    _inherit = "hr.payslip.line"

    amount_base = fields.Char(string='Based on', related='salary_rule_id.amount_base')#, compute='fc_taux')
    # print('amount',amount_base)
