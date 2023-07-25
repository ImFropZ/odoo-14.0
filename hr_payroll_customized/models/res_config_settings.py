from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    threshold = fields.Integer(
        string="Threshold",
        help="Set the threshold of the penalty.",
        config_parameter="hr_payroll_customized.threshold",
        default=1
    )

    deduced_amount = fields.Float(
        string="Deduced Amount",
        help="Set the deduced amount if employee count is more than threshold.",
        config_parameter="hr_payroll_customized.deduced_amount",
        default=0
    )

    monlty_timeoff = fields.Float(
        string="Monlty Timeoff", config_parameter="hr_payroll_customized.monlty_timeoff", default=0)

    overtime_threshold = fields.Float(
        string="Overtime Threshold", help="Set the threshold of overtime e.g 8", config_parameter="hr_payroll_customized.overtime_threshold", default=8)

    @api.model
    def get_deduced_amount_from_settings(self):
        config_parameter_key = 'hr_payroll_customized.deduced_amount'
        deduced_amount = float(self.env['ir.config_parameter'].sudo(
        ).get_param(config_parameter_key, default=0))
        return deduced_amount

    @api.model
    def get_threshold_from_settings(self):
        config_parameter_key = 'hr_payroll_customized.threshold'
        threshold = float(self.env['ir.config_parameter'].sudo(
        ).get_param(config_parameter_key, default=0))
        return threshold

    @api.model
    def get_monlty_timeoff_from_settings(self):
        config_parameter_key = "hr_payroll_customized.monlty_timeoff"
        monlty_timeoff = float(self.env['ir.config_parameter'].sudo(
        ).get_param(config_parameter_key, default=0))
        return monlty_timeoff

    @api.model
    def get_overtime_threshold_from_settings(self):
        config_parameter_key = "hr_payroll_customized.overtime_threshold"
        overtime_threshold = float(self.env['ir.config_parameter'].sudo(
        ).get_param(config_parameter_key, default=8))
        return overtime_threshold
