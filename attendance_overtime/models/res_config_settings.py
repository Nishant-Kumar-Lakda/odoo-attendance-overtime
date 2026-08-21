from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    attendance_overtime_min_minutes = fields.Integer(related='company_id.attendance_overtime_min_minutes', readonly=False)
    attendance_overtime_rounding_minutes = fields.Integer(related='company_id.attendance_overtime_rounding_minutes', readonly=False)
    attendance_overtime_multiplier = fields.Float(related='company_id.attendance_overtime_multiplier', readonly=False)
    attendance_overtime_offday_multiplier = fields.Float(related='company_id.attendance_overtime_offday_multiplier', readonly=False)
    attendance_overtime_hourly_rate = fields.Monetary(related='company_id.attendance_overtime_hourly_rate', readonly=False)
