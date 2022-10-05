# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Payroll - Tunisia",
    "version": "15.0.1.0",
    'description':  """Tunisian Payroll Rules Basic Version.
    ======================
    
        - Configuration of hr_payroll for Tunisian localization
        - Basic configuration for newly installed company
        - Absence - Advances - CNSS 
        - Important: you need to fill the wage amount for the employee in the contract and chose tunisia payroll from the structure field.
        """,
    "category": "Human Resources",
    "website": "",
    "sequence": 38,
    "summary": "Manage your employee payroll records",
    'images': ['static/description/Banner.jpg'],
    "license": "LGPL-3",
    "author": "Asma Mansour",
    "depends": ["hr_contract", "base", "hr", "hr_holidays", "hr_payroll","hr_work_entry","account_accountant", "l10n_tunisia", ],
    "data": [
        "views/hr_employee_views.xml",
        "views/hr_contract_views.xml",
        "views/hr_payslip_views.xml",
        "views/rules_form.xml",
        "data/hr_payroll_data.xml",
        "report/report_payslip.xml",
        "views/company.xml",
        "views/hr_contract_history.xml",

    ],
    "application": True,
}
