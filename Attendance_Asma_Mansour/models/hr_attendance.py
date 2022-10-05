from odoo.addons.hr_attendance.models.hr_attendance import HrAttendance
from odoo import fields, models, api
from datetime import datetime, timedelta
from pytz import timezone


# class ResourceCalendarAttendance(models.Model):
#     _inherit = "resource.calendar.attendance"
#
#     grace_period = fields.Float('Grace Period')

class HrRules(models.Model):
    _inherit = "hr.attendance"
    _description = "Rules Attendances"

    check_in_m = fields.Datetime(string="Sync Check in", store=True, readonly=True, help = "Check in => Work entries")
    check_out_m = fields.Datetime(string="Sync Check out", store=True, readonly=True, help = "Check in => Work entries")
    worked_hours = fields.Float(string='Worked Hours')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    soumis_aux_heures_sup_as = fields.Boolean(string='SUP', related="employee_id.soumis_aux_heures_sup", help= "Salariés soumis aux heures supplémentaires")
    check_in = fields.Datetime(string="Check In")
    check_out = fields.Datetime(string="Check Out")
    moved = fields.Boolean(string="Moved", store=True)
    attendance = fields.Char(string="Attendances", Default="Attendances")
    state = fields.Char(string="State", Default="confirm")
    Validation_heures_supp = fields.Boolean(string="Validation des heures supplémentaires", store=True)

    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Time',
                                           compute='_compute_resource_calendar_id', store=True)

    early_check_in = fields.Float('Av.HT', compute='_compute_early_early_hours', help= "Numbre des heures supplémenatires effectuées avant l'heures de début de travail")

    late_check_out = fields.Float('Ap.HT', compute='_compute_early_early_hours', help= "Numbre des heures supplémenatires effectuées après l'heures de début de travail")
    extra_hours = fields.Float('H.S.', compute='_compute_early_early_hours', help= "Total des heures supplémentaires éffectuées")
    hours_start = fields.Datetime(string="Hours Start", store=True, readonly=True)
    hours_end = fields.Datetime(string="Hours End", compute="fc_hours_end", store=True, readonly=True)

    # Appeler les ressources de calendrier working time
    @api.depends('employee_id')
    def _compute_resource_calendar_id(self):
        for rec in self:
            contracts = rec.employee_id.contract_ids.filtered(lambda x: x.state in ['open'])
            if contracts:
                rec.resource_calendar_id = contracts[0].resource_calendar_id
            else:
                rec.resource_calendar_id = rec.employee_id.resource_calendar_id

    # Calcul des heures sup
    def convert_time_to_float(self, time):
        return time.hour + time.minute / 60


    @api.depends('check_in', 'check_out', 'resource_calendar_id','worked_hours')
    def _compute_early_early_hours(self):
        for rec in self:
            calendar = rec.resource_calendar_id
            if calendar and rec.check_in and rec.check_out:
                a = "2022"
                b = "1"
                c = "1"
                D = ""
                tz = rec.employee_id.tz or rec.resource_calendar_id.tz
                user_timezone = timezone(tz)
                local_timezone = timezone('UTC')
                local_date = local_timezone.localize(rec.check_in).astimezone(timezone(tz))
                number_of_day = str(local_date.weekday())
                days_from_hours = calendar.attendance_ids.filtered(lambda x: x.dayofweek == number_of_day)
                hours_converted = self.convert_time_to_float(local_date)

                hours_converted = round(hours_converted, 2)
                day_start = rec.check_in.strftime('%Y-%m-%d 00:00:00.%f')
                day_end = rec.check_in.strftime('%Y-%m-%d 23:59:59.%f')
                for day in days_from_hours:

                    in_hour = int(day.hour_from)
                    print("in_hour", in_hour)
                    out_hour = int(day.hour_to)
                    print("out_hour", out_hour)

                    in_min = int((in_hour - int(in_hour)) * 60)
                    print("in_min", in_min)
                    out_min = int((out_hour - int(out_hour)) * 60)
                    print("out_min", out_min)
                    out_hour1 = int(days_from_hours[0].hour_to)
                    print("out_hour1", out_hour1)
                    out_min1 = int((days_from_hours[0].hour_to - int(days_from_hours[0].hour_to)) * 60)
                    print("out_min1", out_min1)
                    check_out = user_timezone.localize(rec.check_out.replace(hour=out_hour, minute=out_min)).astimezone(timezone('UTC'))
                    print("check_out", check_out)
                    check_out1 = user_timezone.localize(
                        rec.check_out.replace(hour=out_hour1, minute=out_min1)).astimezone(timezone('UTC'))
                    print("check_out1", check_out1)
                    work_day_start = user_timezone.localize(
                        rec.check_in.replace(hour=in_hour, minute=in_min)).astimezone(timezone('UTC')) #- timedelta(seconds=2)
                    print("work_day_start:", work_day_start)
                    B = work_day_start.strftime('%Y-%m-%d %H:00:00')
                    print("B:", B)
                    print("work_day_start", work_day_start)

                    if day.hour_to > hours_converted and day.day_period == 'morning':  # and matched_recs and rec.id == matched_recs.ids[0]:

                        print("day.day_period", day.day_period)
                        early_mins = day.hour_from - hours_converted
                        print("day.hour_from", day.hour_from)
                        print("day.hour_to", day.hour_to)
                        print("hours_converted", hours_converted)
                        print("early_mins", early_mins)
                        if early_mins > 0:
                            rec.early_check_in = early_mins
                            early_min = early_mins
                        else:
                            rec.early_check_in = 0
                            early_min = 0

                    if day.hour_to >= hours_converted and day.day_period == 'morning':
                        if day.hour_from <= hours_converted <= (day.hour_from + 0.5):
                            rec.check_in_m = B
                        else:
                            rec.check_in_m = rec.check_in
                    elif day.hour_from < hours_converted and day.day_period == 'afternoon':
                        rec.check_in_m = rec.check_in
                    elif day.hour_from < hours_converted and (day.day_period is not 'afternoon') and (day.day_period is not 'morning'):
                        rec.check_in_m = rec.check_in

                # print("X:", x)

                rec.check_in_m = rec.check_in_m
                rec.early_check_in = rec.early_check_in

                # Les heures supp après check out
                work_day_end = ''
                check_in = rec.check_in
                local_date_to = local_timezone.localize(rec.check_out).astimezone(timezone(self.env.user.tz))
                print("timezone(self.env.user.tz):", timezone(self.env.user.tz))
                local_date_to = local_date_to.replace(second=0, microsecond=0)
                hours_to_converted = self.convert_time_to_float(local_date_to)
                hours_to_converted = round(hours_to_converted, 2)
                not_ordered_days_to_hours = calendar.attendance_ids.filtered(lambda x: x.dayofweek == number_of_day)
                days_to_hours = self.env['resource.calendar.attendance'].search(
                    [('id', 'in', not_ordered_days_to_hours.ids)], order='hour_from')
                early_checkout = 0
                flag = True
                for day in days_to_hours:

                    out_hour = day.hour_to
                    out_min = int((out_hour - int(out_hour)) * 60)
                    # work_day_end = user_timezone.localize(rec.check_out.replace(hour=int(out_hour), minute=out_min))
                    att = self.env['hr.work.entry.type'].search(
                        [('name', '=', "Work Calendar")])
                    print("id", att.id)
                    out_hour = day.hour_to
                    out_min = int((out_hour - int(out_hour)) * 60)
                    check_out = user_timezone.localize(
                        rec.check_out.replace(hour=out_hour1, minute=out_min)).astimezone(timezone('UTC')) - timedelta(
                        seconds=2)
                    print("check_out", check_out)  # print("",)
                    att_after_checkout = self.search([('check_in', '>', check_in),
                                                      ('check_in', '<', check_out),
                                                      ('employee_id', '=', rec.employee_id.id)])
                    print("att_after_checkout", att_after_checkout)
                    if not att_after_checkout:

                        matched_early_recs = self.search([('check_in', '>', day_start),
                                                          ('check_out', '<', check_out),
                                                          ('employee_id', '=', rec.employee_id.id)],
                                                         order='check_in asc')
                        print("matched_early_recs", matched_early_recs)
                        work_day_end = user_timezone.localize(
                            rec.check_out.replace(hour=int(out_hour), minute=out_min)).astimezone(
                            timezone('UTC')) - timedelta(seconds=2)
                        print("work_day_end", work_day_end)

                        if hours_to_converted > day.hour_from:
                            out_hour = int(day.hour_to)
                            print("out_hour", out_hour)

                            out_min = int((out_hour - int(out_hour)) * 60)
                            print("out_min", out_min)
                            work_day_end = user_timezone.localize(rec.check_out.replace(hour=int(out_hour), minute=out_min)).astimezone(timezone('UTC'))# - timedelta(seconds=2)
                            print("work_day_end:", work_day_end)
                            # work_day_end = work_day_end.strftime('%Y-%m-%d %H:00:00')
                            print("D:", work_day_end)

                            early_checkout = hours_to_converted - day.hour_to
                            print("early_checkout:", early_checkout)
                            print("day.hour_to:", day.hour_to)
                            date = work_day_end.date()
                            # time = day.hour_to.time()
                            a = str(date).split("-")[0]
                            print("a:", a)
                            b = str(date).split("-")[1]
                            # b1 = str(record.date_to)[5:7]
                            c = str(date).split("-")[2]
                            # d = str(time).split(":")[0]

                            # if (day.hour_to - 0.5) <= hours_to_converted <= day.hour_to and int(a) > 0 and int(
                            #         b) > 0 and int(c) > 0 and int(day.hour_to) > 0:
                            #     rec.check_out_m = datetime(int(a), int(b), int(c), int(day.hour_to), 0, 0)
                            #     d = int(day.hour_to)
                            # else:
                            #     rec.check_out_m = rec.check_out
                            #     d = int(day.hour_to)
                            work_day_end = work_day_end.strftime('%Y-%m-%d %H:00:00')
                            D= work_day_end
                            if (day.hour_to - 0.5) <= hours_to_converted <= day.hour_to:
                                rec.check_out_m = work_day_end

                            else:
                                rec.check_out_m = rec.check_out
                        # elif hours_to_converted == day.hour_to:
                        #     rec.check_out_m = rec.check_out


                print("Y:", rec.check_out_m)
                rec.check_out_m = rec.check_out_m

                rec.hours_start = D

                rec.late_check_out = early_checkout if early_checkout > 0 else 0

                rec.extra_hours = int(rec.late_check_out) + int(rec.early_check_in) if rec.soumis_aux_heures_sup_as == True and rec.worked_hours>9.4 else 0

                print(type(work_day_end))
                print("rec.soumis_aux_heures_sup_as", rec.soumis_aux_heures_sup_as)
                print("rec.extra_hours", rec.extra_hours)
                print("rec.late_check_out", rec.late_check_out)


            else:
                rec.late_check_out = 0
                rec.early_check_in = 0
                rec.extra_hours = 0


    @api.depends('extra_hours', 'hours_start')
    def fc_hours_end(self):
        for rec in self:
            if rec.hours_start is not False:
                date= rec.hours_start.date()
                time = rec.hours_start.time()

                a = str(date).split("-")[0]
                print("a:",a)
                b = str(date).split("-")[1]
                # b1 = str(record.date_to)[5:7]
                c = str(date).split("-")[2]
                d= str(time).split(":")[0]
                e= str(time).split(":")[1]
                f= str(time).split(":")[2]
                cc = datetime(int(a), int(b), int(c), int(d), int(e), int(f)) + timedelta(hours=int(rec.extra_hours))
                print("cc:", cc)
                print("cc:", type(cc))
                print("timedelta:", timedelta(hours=int(rec.extra_hours)))
                rec.hours_end= cc





    # Action de synchronisation entre attendance et time off
    def action_attendance_sync(self):
        # messages = ""
        for rec in self.sorted(key=lambda l: l.employee_id):
            hr_holidays = self.env['hr.leave']
            timeoff = self.env['hr.leave.type'].search(
                [('name', '=', "Attendances")])
            print(timeoff.id)
            vals = {
                    'employee_id': rec.employee_id.id,
                    'date_from': rec.check_in_m,
                    'date_to': rec.check_out_m,
                    'holiday_status_id': timeoff.id,
                }
            hr_holidays = hr_holidays.sudo().create(vals)

            if hr_holidays:
                # rec.moved = True
                rec.sudo().write({
                    'moved': True,
                })
