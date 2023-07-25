from odoo import fields, api, models


class HrAttendanceCustomized(models.Model):
    _inherit = "hr.attendance"

    count = fields.Integer(string="Count", store=True,
                           compute="_compute_count")

    check_in = fields.Datetime(required=False)
    check_out = fields.Datetime(required=False)

    @api.depends("check_in", "check_out")
    def _compute_count(self):
        for record in self:
            count = 0
            if (not record.check_in):
                count = count + 1

            if (not record.check_out):
                count = count + 1

            record.count = count

    # Overwrite validation from hr attendance
    def _check_validity(self):
        pass
