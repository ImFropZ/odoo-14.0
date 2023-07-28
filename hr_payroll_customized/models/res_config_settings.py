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

    overtime_threshold = fields.Float(
        string="Overtime Threshold", help="Set the threshold of overtime e.g 8", config_parameter="hr_payroll_customized.overtime_threshold", default=8)

    late_check_in = fields.Float(
        string="Late Check-in", help="Set late duration after work check-in", config_parameter="hr_payroll_customized.late_check_in", default=0)

    early_check_out = fields.Float(
        string="Early Check-out", help="Set early duration before work check-out", config_parameter="hr_payroll_customized.early_check_out", default=0)

    @api.model
    def get_deduced_amount_from_settings(self):
        config_parameter_key = 'hr_payroll_customized.deduced_amount'
        return float(self.env['ir.config_parameter'].sudo().get_param(config_parameter_key, default=0))

    @api.model
    def get_threshold_from_settings(self):
        config_parameter_key = 'hr_payroll_customized.threshold'
        return float(self.env['ir.config_parameter'].sudo().get_param(config_parameter_key, default=0))

    @api.model
    def get_overtime_threshold_from_settings(self):
        config_parameter_key = "hr_payroll_customized.overtime_threshold"
        return float(self.env['ir.config_parameter'].sudo().get_param(config_parameter_key, default=8))

    @api.model
    def get_late_check_in_from_settings(self):
        config_parameter_key = "hr_payroll_customized.late_check_in"

        return float(self.env['ir.config_parameter'].sudo().get_param(config_parameter_key, default=0))

    @api.model
    def get_early_check_out_from_settings(self):
        config_parameter_key = "hr_payroll_customized.early_check_out"

        return float(self.env['ir.config_parameter'].sudo().get_param(config_parameter_key, default=0))

    @api.constrains("late_check_in", "early_check_out")
    def _check_validation_hour(self):
        if self.late_check_in < 0:
            self.late_check_in = 0

        if self.early_check_out < 0:
            self.early_check_out = 0
