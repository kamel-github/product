from odoo.addons.hr_attendance.models.hr_attendance import HrAttendance
from odoo import fields, models, api
from datetime import datetime, timedelta

class Hrtimeoffattendance(models.Model):
    _inherit = "hr.leave"
    _description = "Attendances"

    work_hours = fields.Float(string='Work Hours', related="employee_id.attendance_ids.worked_hours")

