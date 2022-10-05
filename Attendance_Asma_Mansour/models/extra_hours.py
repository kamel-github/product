# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime, timedelta
from operator import itemgetter

import pytz
from odoo import models, fields, api, exceptions, _
from odoo.tools import format_datetime
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv.expression import AND, OR
from odoo.tools.float_utils import float_is_zero
class HrAttendanceExtraHours(models.Model):
    _inherit = "hr.attendance"
    employee_id = fields.Many2one(string="Employee")

class HrAttendanceExtraHours(models.Model):
    # _inherit = "hr.attendance"
    _name = "extra.hours"
    _description = "Extra Hours"


    # Fiche de paie

    payslip_id = fields.Many2one('hr.payslip', string="Payslip", ondelete='set null')

    @api.model_create_multi
    def create(self, vals_list):
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        payslip_ids = [i for i in set([d.get('payslip_id', 0) for d in vals_list]) if i != 0]
        if payslip_ids:
            payslips = self.env['hr.payslip'].sudo().browse(payslip_ids)
            if payslips.filtered(lambda p: p.state not in ('draft', 'verify')):
                raise ValidationError('Cannot create attendance linked to payslip that is not draft.')
        return super().create(vals_list)

    def write(self, values):
        payslip_id = values.get('payslip_id')
        if payslip_id:
            payslip = self.env['hr.payslip'].sudo().browse(payslip_id)
            if payslip.exists().state not in ('draft', 'verify'):
                raise ValidationError('Cannot modify attendance linked to payslip that is not draft.')
        return super().write(values)

    def unlink(self):
        attn_with_payslip = self.filtered(lambda a: a.payslip_id)
        attn_with_payslip.write({'payslip_id': False})
        return super(HrAttendanceExtraHours, self - attn_with_payslip).unlink()



    # Work entry
    work_type_id = fields.Many2one('hr.work.entry.type', string='Work Type',
                                   default=lambda self: self.env.ref('hr_attendance_work_entry.work_input_attendance',
                                                                     raise_if_not_found=False))

    @api.model
    def gather_attendance_work_types(self):
        work_types = self.env['hr.work.entry.type'].sudo().search([('allow_attendance', '=', True)])
        return work_types.read(['id', 'name', 'attendance_icon'])

    # # Fiche de paie


    employee_id = fields.Many2one('hr.employee', string="Employee") #, default=_default_employee, ,ondelete='cascade', index=True

    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
        readonly=True)
    hours_start = fields.Datetime(string="Hours Start", required=True,tracking=True) #default=fields.Datetime.now,

    hours_end = fields.Datetime(string="Hours End", copy=False, tracking=True)
    extra_hours = fields.Float(string='Extra Hours',  store=True, readonly=True, compute='_compute_extra_hours')

    def name_get(self):
        result = []
        for attendance in self:
            if not attendance.hours_end:
                result.append((attendance.id, _("%(empl_name)s from %(hours_start)s") % {
                    'empl_name': attendance.employee_id.name,
                    'hours_start': format_datetime(self.env, attendance.hours_start, dt_format=False),
                }))
            else:
                result.append((attendance.id, _("%(empl_name)s from %(hours_start)s to %(hours_end)s") % {
                    'empl_name': attendance.employee_id.name,
                    'hours_start': format_datetime(self.env, attendance.hours_start, dt_format=False),
                    'hours_end': format_datetime(self.env, attendance.hours_end, dt_format=False),
                }))
        return result

    @api.depends('hours_start', 'hours_end')
    def _compute_extra_hours(self):
        for attendance in self:
            if attendance.hours_end and attendance.hours_start:
                delta = attendance.hours_end - attendance.hours_start
                attendance.extra_hours = delta.total_seconds() / 3600.0
            else:
                attendance.extra_hours = False




    # def copy_data(self, default=None):
    #     if default and 'hours_start' in default and 'hours_end' in default:
    #         default['hours_start'] = default.get('hours_start')
    #         default['hours_end'] = default.get('hours_end')
    #         return super().copy_data(default)
    #     raise UserError(_('An Extra Hours cannot be duplicated.'))

    # @api.onchange('date_from')
    # def validate_extra_hours(self):
    #
    #     if self.hours_start:
    #         if self.hours_start < fields.Date.today():
    #             raise UserError(
    #                 _("You cannot duplicate an Extra Hours."))
        #     if self.date_to and self.date_to < self.date_from:
        #         raise UserError(_("Please enter End Date correctly. End date should't be smaller than start date."))
        # elif self.date_to and self.date_to < fields.Date.today():
        #     raise UserError(_("Please enter End Date correctly. End date should't be smaller than current date."))

    @api.constrains('hours_start', 'hours_end')
    def _check_validity_hours_start_hours_end(self):
        """ verifies if check_in is earlier than check_out. """
        for attendance in self:
            if attendance.hours_start and attendance.hours_end:
                if attendance.hours_end < attendance.hours_start:
                    raise exceptions.ValidationError(_('"Hours End" time cannot be earlier than "Hours Start" time.'))

    @api.constrains('hours_start', 'hours_end', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without hours_end)
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our hours_start time and check it doesn't overlap with ours
            last_attendance_before_hours_start = self.env['extra.hours'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('hours_start', '<=', attendance.hours_start),
                ('id', '!=', attendance.id),
            ], order='hours_start desc', limit=1)
            if last_attendance_before_hours_start and last_attendance_before_hours_start.hours_end and last_attendance_before_hours_start.hours_end > attendance.hours_start:
                raise exceptions.ValidationError(
                    _("Cannot create new extra hours record for %(empl_name)s, record has been already created on %(datetime)s") % {
                        'empl_name': attendance.employee_id.name,
                        'datetime': format_datetime(self.env, attendance.hours_start, dt_format=False),
                    })

            if not attendance.hours_end:
                # if our attendance is "open" (no hours_end), we verify there is no other "open" attendance
                no_hours_end_attendances = self.env['extra.hours'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('hours_end', '=', False),
                    ('id', '!=', attendance.id),
                ], order='hours_start desc', limit=1)
                if no_hours_end_attendances:
                    raise exceptions.ValidationError(
                        _("Cannot create new extra hours record for %(empl_name)s, record has been already created  since %(datetime)s") % {
                            'empl_name': attendance.employee_id.name,
                            'datetime': format_datetime(self.env, no_hours_end_attendances.hours_start, dt_format=False),
                        })
            else:
                # we verify that the latest attendance with hours_start time before our hours_end time
                # is the same as the one before our hours_start time computed before, otherwise it overlaps
                last_attendance_before_hours_end = self.env['extra.hours'].search([
                    ('employee_id', '=', attendance.employee_id.id),
                    ('hours_start', '<', attendance.hours_end),
                    ('id', '!=', attendance.id),
                ], order='hours_start desc', limit=1)
                if last_attendance_before_hours_end and last_attendance_before_hours_start != last_attendance_before_hours_end:
                    raise exceptions.ValidationError(
                        _("Cannot create new extra hours record for %(empl_name)s, record has been already created on %(datetime)s") % {
                            'empl_name': attendance.employee_id.name,
                            'datetime': format_datetime(self.env, last_attendance_before_hours_end.hours_start,
                                                        dt_format=False),
                        })

    @api.returns('self', lambda value: value.id)
    def copy(self):
            raise exceptions.UserError(_('You cannot duplicate an Extra Hours.'))


    @api.model  # ('name','employee_id')
    def default_get(self, fields):

        res = super(HrAttendanceExtraHours, self).default_get(fields)
        active_id = self._context.get('active_id')
        # id_check_in = self._context.get('check_in')
        # record = self.env['hr.attendance'].search([('employee_id', '=', 'employee_id')])
        selected_record = self.env['hr.attendance'].browse(active_id)
        print("record",selected_record)


        list = []
        for rec in selected_record:

            print("slected record", rec)
            list.append(rec.ids)
            print("list:",rec.ids)

            if active_id:
                print("blaaaa", active_id)
                # selected_record = self.env['hr.attendance'].search([('employee_id', '=', id_name)])
                print('nom:', rec.employee_id.name)
                res['employee_id'] = rec.employee_id
                res['hours_start'] = rec.hours_start
                res['hours_end'] = rec.hours_end
                res['extra_hours'] = rec.extra_hours
                res['work_type_id'] = self.env['hr.work.entry.type'].search([('name', '=', "Extra Hours 175%")])
                print('hours_start:', rec.hours_start)
                print('hours_end:', rec.hours_end)
                print('extra_hours:', rec.check_out)

                    # hours = self.env['extra.hours'].search(['hours_start', '=', rec.hours_start])
                    # print('hours:', hours)
                    # if hours != rec.id:
                        # for h in hours:
                        #     if h.id != rec.id:


            return res


