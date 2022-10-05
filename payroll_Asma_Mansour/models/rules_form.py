from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError

class HrRules(models.Model):
    _inherit = "hr.salary.rule"
    _description = "Rules"

    nombre_des_heures = fields.Boolean(string='Nombre des heures ou des jours', default=False,
                                        help="Used to display the salary rule on payslip.")
    retenues = fields.Boolean(string='Retenues', default=False,
                                       help="Used to display the salary rule on payslip.")
    remuneration = fields.Boolean(string='Rémunération', default=False,
                                       help="Used to display the salary rule on payslip.")
    amount_base = fields.Char(string='based on', help='result will be affected to a variable')#,comptue='compute_base_on'
    base = fields.Char(string="Base")

    def _compute_rule(self, localdict):

        """
        :param localdict: dictionary containing the current computation environment
        :return: returns a tuple (amount, qty, rate)
        :rtype: (float, float, float)
        """
        self.ensure_one()
        if self.amount_base and self.base:
            try:
                return (float(safe_eval(self.amount_base, localdict)), 100, float(safe_eval(self.base, localdict)))
            except Exception as e:
                self._raise_error(localdict, _("Wrong percentage base or quantity defined for:"), e)
                # rec.base = float(safe_eval(self.amount_base, localdict))
        print("base", self.base)
        print("amount base:",self.amount_base)
        print(self.quantity)

        if self.amount_select == 'fix':
            try:
                return self.amount_fix or 0.0, float(safe_eval(self.quantity, localdict)), 100.0
            except Exception as e:
                self._raise_error(localdict, _("Wrong quantity defined for:"), e)
        if self.amount_select == 'percentage':
            try:
                return (float(safe_eval(self.amount_percentage_base, localdict)),
                        float(safe_eval(self.quantity, localdict)),
                        self.amount_percentage or 0.0)
            except Exception as e:
                self._raise_error(localdict, _("Wrong percentage base or quantity defined for:"), e)

        # if self.amount_base:
        #     try:
        #         return (float(safe_eval(self.amount_base, localdict)),float(safe_eval(self.quantity, localdict)),
        #                 self.amount_percentage or 0.0)
        #     except Exception as e:
        #         self._raise_error(localdict, _("Wrong percentage base or quantity defined for:"), e)
        #         # rec.base = float(safe_eval(self.amount_base, localdict))
        #
        # print('amount', self.amount_base)
        # if self.amount_base:
        #     try:
        #         return (float(safe_eval(self.amount_base, localdict)), float(safe_eval(self.quantity, localdict)),
        #                 self.base or 0.0)
        #     except Exception as e:
        #         self._raise_error(localdict, _("Wrong percentage base or quantity defined for:"), e)
        #         # rec.base = float(safe_eval(self.amount_base, localdict))
        #     print("base", self.Base)

        else:  # python code
            try:
                safe_eval(self.amount_python_compute or 0.0, localdict, mode='exec', nocopy=True)
                print("safe_eval",safe_eval(self.amount_python_compute or 0.0, localdict, mode='exec', nocopy=True))

                return float(localdict['result']), localdict.get('result_qty', 1.0), localdict.get('result_rate', 100.0)
                print("comp",float(localdict['result']), localdict.get('result_qty', 1.0), localdict.get('result_rate', 100.0))
            except Exception as e:
                self._raise_error(localdict, _("Wrong python code defined for:"), e)

            # try:
            #     return (float(safe_eval(self.amount_base, localdict)), float(safe_eval(self.quantity, localdict)),
            #             self.amount_percentage or 0.0)
            # except Exception as e:
            #     self._raise_error(localdict, _("Wrong percentage base or quantity defined for:"), e)
            #     # rec.base = float(safe_eval(self.amount_base, localdict))


