from odoo import fields, api, models
import math
from itertools import groupby


class HrPayslipCustomized(models.Model):
    _inherit = "hr.payslip"

    count = fields.Integer(string="Count", readonly=True,
                           compute="_compute_count")

    extra_paid_amount = fields.Float(string="Extra Paid Amount", readonly=True)
    deduced_paid_amount = fields.Float(
        string="Deduced Paid Amount", readonly=True)

    paid_amount = fields.Float(
        string="Paid Amount", readonly=True)

    # Additional Fields
    # National Holiday Fields
    national_holiday_count = fields.Integer(
        string="National Holiday OT Count", readonly=True)
    national_holiday_paid = fields.Float(
        string="National Holiday Paid Amount", readonly=True)

    # Timeoff Fields
    timeoff_count = fields.Float(
        string="Timeoff left over count", readonly=True)
    timeoff_paid = fields.Float(string="Timeoff Paid Amount", readonly=True)

    # Overtime Fields
    overtime_count = fields.Float(
        string="Overtime hour(s)", readonly=True)
    overtime_paid = fields.Float(string="Overtime Paid Amount", readonly=True)

    # Deduced Fields
    # Missed Finger Print Fields
    missed_finger_print_count = fields.Integer(
        string="Missed Finger Print", readonly=True)
    missed_finger_print_paid = fields.Float(
        string="Missed Finger Print Paid Amount", readonly=True)

    # Late Check-in, Early Check-out fields
    late_check_in_count = fields.Integer(string="Late Check-in", readonly=True)
    early_check_in_count = fields.Integer(
        string="Early Check-out", readonly=True)
    late_check_in_and_early_check_out_paid_amount = fields.Float(
        string="Late Check-in Early Check-out Paid Amount", readonly=True)

    # លំហែបិតុភាព កាត់

    @api.depends("employee_id", "date_from", "date_to")
    def _compute_count(self):
        if not self.employee_id:
            self.count = 0
            return

        self._calculate_extra_bonus()

        self._calculate_penalty()

        self.count = 0

    def _integer_to_day_name(self, index_day_of_week) -> str:
        day_names = ['Monday', 'Tuesday', 'Wednesday',
                     'Thursday', 'Friday', 'Saturday', 'Sunday']
        return day_names[int(index_day_of_week)]

    def _calculate_extra_bonus(self):
        # Calculate national holiday overtime
        self._calculate_national_holiday()

        # Calculate the work in dayoff
        self._calculate_dayoff_work()

        # Calculate the overtime
        self._calculate_overtime()

        # Caclulate bonus paid amount
        self._calculate_bonus_paid_amount()

    def _calculate_penalty(self):
        self._calculate_missed_finger_print()

        self._calculate_late_check_in_and_early_check_out()

        self._calculate_deduced_paid_amount()

    # Return current employee attendance records
    def _get_attendance_records(self):
        return self.env["hr.attendance"].search([
            '|',
            '&',
            ('check_in', '>=', self.date_from),
            ('employee_id', '=', self.employee_id.id),
            '&',
            ('check_out', '<=', self.date_to),
            ('employee_id', '=', self.employee_id.id),
        ])

    # Return current employee timeoff
    def _get_employee_timeoff(self):
        return self.env['hr.leave'].search([
            ("employee_id", "=", self.employee_id.id),
            ("date_from", ">=", self.date_from),
            ("date_to", "<=", self.date_to),
            ("state", "=", "validate")
        ])

    # Return number of days between date_from to date_to
    def _get_days(self):
        if self.date_to and self.date_from:
            timedelta = self.date_to - self.date_from
            return timedelta.days
        return 1

    # Return average salary of current employee
    def _get_salary_avg_day(self):
        return self._get_salary() / self._get_days()

    # Return salary of current employee
    def _get_salary(self):
        return sum(self.worked_days_line_ids.mapped("amount"))

    # Calculate the dayoff
    def _calculate_dayoff_work(self):
        settings = self.env['res.config.settings'].create({})
        setting_monlty_timeoff = settings.get_monlty_timeoff_from_settings()

        # NOTE: Duration Display from timeoff is format like this e.g. 1.5 days
        self.timeoff_count = max(
            0, setting_monlty_timeoff - float(self._get_employee_timeoff().duration_display.split(' ')[0]))

        if self.timeoff_count > 0:
            self.timeoff_paid = self._get_salary_avg_day() * self.timeoff_count
        else:
            self.timeoff_paid = 0

    # Calculate the overtime
    def _calculate_overtime(self):
        settings = self.env['res.config.settings'].create({})

        setting_overtime_threshold = settings.get_overtime_threshold_from_settings()

        for attendance in self._get_attendance_records():
            worked_hours = max(0, attendance.worked_hours -
                               setting_overtime_threshold)
            self.overtime_count += worked_hours

        self.overtime_paid = self._get_salary_avg_day() / 8 * 3 * self.overtime_count

    # Calculate the national holiday overtime
    def _calculate_national_holiday(self):
        national_holiday_obj = self.employee_id.resource_calendar_id.global_leave_ids
        national_holiday_records = national_holiday_obj.search([])

        national_holiday_count = 0

        for national_holiday in national_holiday_records:
            national_holiday_date_from = national_holiday.date_from.date()
            national_holiday_date_to = national_holiday.date_to.date()

            for attendance in self._get_attendance_records():
                attendance_date = attendance.check_in.date()

                if national_holiday_date_from <= attendance_date < national_holiday_date_to:
                    national_holiday_count += 1

        self.national_holiday_count = national_holiday_count
        self.national_holiday_paid = self._get_salary_avg_day() * national_holiday_count

    # Add bonus money to extra_paid_amount
    def _calculate_bonus_paid_amount(self):
        self.extra_paid_amount = self.national_holiday_paid + \
            self.timeoff_paid + self.overtime_paid

    # Calculate the missed finger print
    def _calculate_missed_finger_print(self):
        settings = self.env['res.config.settings'].create({})

        self.missed_finger_print_count = sum(
            self._get_attendance_records().mapped('count'))

        # Getting threshold and deduced amount from settings
        setting_threshold = settings.get_threshold_from_settings()
        setting_deduced_amount = settings.get_deduced_amount_from_settings()

        self.missed_finger_print_paid = math.floor(
            self.count / setting_threshold) * setting_deduced_amount

    # Calculate the late check-in and early check-out
    def _calculate_late_check_in_and_early_check_out(self):
        settings = self.env['res.config.settings'].create({})

        # Getting threshold and deduced amount from settings
        setting_late_check_in = settings.get_late_check_in_from_settings()
        setting_early_check_out = settings.get_early_check_out_from_settings()

        late_check_in_count = 0
        early_check_out_count = 0

        worked_day_records = self.employee_id.resource_calendar_id.attendance_ids
        group_worked_day_records = groupby(
            worked_day_records, key=lambda rec: rec.dayofweek)
        group_worked_day_records_dist = {
            key: list(worked_day) for key, worked_day in group_worked_day_records}

        for attendance in self._get_attendance_records():
            day_of_week_index = attendance.check_in.weekday()

            current_attendace_worked_records = group_worked_day_records_dist.get(
                str(day_of_week_index), [])

            # If the worked have 2 shifts
            if len(current_attendace_worked_records) == 2:
                for worked_day in current_attendace_worked_records:
                    if worked_day.day_period == "morning":
                        check_in_time = attendance.check_in.hour + attendance.check_in.minute / 60
                        if check_in_time - worked_day.hour_from > setting_late_check_in:
                            late_check_in_count += 1
                    else:
                        if not (attendance.check_out):
                            continue
                        check_out_time = attendance.check_out.hour + attendance.check_out.minute / 60
                        if worked_day.hour_to - check_out_time > setting_early_check_out:
                            early_check_out_count += 1

            # Checking 1 shifts
            elif len(current_attendace_worked_records) == 1:
                worked_day = current_attendace_worked_records[0]

                check_in_time = attendance.check_in.hour + attendance.check_in.minute / 60
                if check_in_time - worked_day.hour_from > setting_late_check_in:
                    late_check_in_count += 1

                if attendance.check_out:
                    check_out_time = attendance.check_out.hour + attendance.check_out.minute / 60
                    if worked_day.hour_to - check_out_time > setting_early_check_out:
                        early_check_out_count += 1


        print(f"Check In Late: {late_check_in_count}")
        print(f"Check Out Early: {early_check_out_count}")

        self.late_check_in_count = late_check_in_count
        self.early_check_out_count = early_check_out_count
        self.late_check_in_and_early_check_out_paid_amount = self._get_salary_avg_day / \
            8 * (late_check_in_count + early_check_out_count)

    def _calculate_deduced_paid_amount(self):
        self.deduced_paid_amount = self.missed_finger_print_paid + self.late_check_in_and_early_check_out_paid_amount