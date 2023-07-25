from odoo import fields, api, models
import math


class HrPayslipCustomized(models.Model):
    _inherit = "hr.payslip"

    count = fields.Integer(string="Count", readonly=True,
                           compute="_compute_count")

    paid_amount = fields.Float(
        string="Paid Amount", readonly=True)

    # National Holiday Fields
    national_holiday_count = fields.Integer(
        string="National Holiday OT Count", readonly=True)
    national_holiday_amount = fields.Float(
        string="National Holiday Paid Amount", readonly=True)

    # Timeoff Fields
    timeoff_count = fields.Float(
        string="Timeoff left over count", readonly=True)
    timeoff_paid = fields.Float(string="Timeoff Paid Amount", readonly=True)

    # Overtime Fields
    overtime_count = fields.Float(
        string="Overtime hour(s)", readonly=True)
    overtime_paid = fields.Float(string="Overtime Paid Amount", readonly=True)

    @api.depends("employee_id", "date_from", "date_to")
    def _compute_count(self):
        if not self.employee_id:
            self.count = 0
            return

        # Create settings object
        settings = self.env['res.config.settings'].create({})
        # Calculate the total amount
        month_amount = sum(self.worked_days_line_ids.mapped("amount"))

        self.count = sum(self._get_attendance_records().mapped('count'))

        # Getting threshold and deduced amount from settings
        setting_threshold = settings.get_threshold_from_settings()
        setting_deduced_amount = settings.get_deduced_amount_from_settings()

        self.paid_amount = month_amount - (
            math.floor(self.count / setting_threshold) * setting_deduced_amount
        )

        # Calculate national holiday overtime
        self._calculate_national_holiday()

        # Calculate the work in dayoff
        self._calculate_dayoff_work()

        # Calculate the overtime
        self._calculate_overtime()


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

    # Return average salary of current employee
    def _get_salary_avg_day(self):
        month_amount = sum(self.worked_days_line_ids.mapped("amount"))
        return month_amount / 30

    # Calculate the dayoff paid amount
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

    # Calculate the overtime paid amount
    def _calculate_overtime(self):
        settings = self.env['res.config.settings'].create({})

        setting_overtime_threshold = settings.get_overtime_threshold_from_settings()

        for attendance in self._get_attendance_records():
            print(attendance.worked_hours)
            worked_hours = max(0, attendance.worked_hours -
                               setting_overtime_threshold)
            self.overtime_count += worked_hours

        self.overtime_paid = self._get_salary_avg_day() / 8 * 3 * self.overtime_count

    # Calculate the national holiday overtime paid amount
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
                    print(
                        f"{national_holiday.name} : {national_holiday_date_from} - {national_holiday_date_to}")
                    national_holiday_count += 1

        self.national_holiday_count = national_holiday_count
        self.national_holiday_amount = self._get_salary_avg_day() * national_holiday_count
