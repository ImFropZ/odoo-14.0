from odoo import fields, api, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    timeoff_limits = fields.Integer(string="Timeoff Limits", default=0)

    @api.constrains("timeoff_limits")
    def _validate_timeoff_limits(self):
        if self.timeoff_limits < 0:
            self.timeoff_limits = abs(self.timeoff_limits)
