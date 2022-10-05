{
    'name': 'Payroll Overtime',
    'description': 'Provide mechanisms to calculate overtime.',
    'version': '15.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'data': [
        'security/ir.model.access.csv',
        'data/overtime_data.xml',
    ],
    'depends': [
        'hr_payroll',
        'hr_work_entry',
        'hr_work_entry_contract_enterprise',  # only for menu!
    ],
}
