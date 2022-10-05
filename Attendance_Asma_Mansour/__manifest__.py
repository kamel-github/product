# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Attendances",
    "version": "15.0.0.0",
    'description':  """Attendances Basic Version.
    ======================
    
   
        """,
    "category": "Human Resources",
    "website": "",
    "sequence": 40,
    "summary": "Manage your employee attendance records",
    'images': ['static/description/attendance.jpg'],
    "license": "LGPL-3",
    "author": "Asma Mansour",
    "depends": ["hr_attendance", "base", "hr","payroll_Asma_Mansour", "hr_holidays","hr_payroll","web_gantt", "hr_work_entry","hr_payroll_overtime"],
    "data": [

        "security/ir.model.access.csv",
        "wizard/extra_hours_wizard.xml",
        "views/extra_hours.xml",
        "views/hr_attendance.xml",
        "views/hr_work_entry.xml",
        "views/hr_time_off.xml",
        "views/menu.xml",
        "views/work_entry_views.xml",
        "views/hr_payslip_views.xml",
        "data/action.xml",
        "data/hr_leave_data.xml",
        "data/hr_attendance_work_entry_data.xml",





    ],
    "application": True,
}
