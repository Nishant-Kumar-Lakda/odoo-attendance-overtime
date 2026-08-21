from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    attendance_overtime_min_minutes = fields.Integer(string='Minimum Overtime (Minutes)', default=30, help='Minimum overtime duration required before an overtime record is generated.')
    attendance_overtime_rounding_minutes = fields.Integer(string='Overtime Rounding (Minutes)', default=15, help='Round overtime down to this interval. Use 0 to disable rounding.')
    attendance_overtime_multiplier = fields.Float(string='Regular Overtime Multiplier', default=1.5, digits=(16, 2))
    attendance_overtime_offday_multiplier = fields.Float(string='Off-Day Overtime Multiplier', default=2.0, digits=(16, 2))
    attendance_overtime_hourly_rate = fields.Monetary(string='Default Overtime Hourly Rate', currency_field='currency_id', help='Used when an employee does not have a specific overtime hourly rate.')
