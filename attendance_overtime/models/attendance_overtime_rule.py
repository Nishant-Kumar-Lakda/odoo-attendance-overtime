from odoo import fields, models


class AttendanceOvertimeRule(models.Model):
    _name = 'attendance.overtime.rule'
    _description = 'Attendance Overtime Rule'
    _order = 'sequence, id'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, index=True)
    minimum_minutes = fields.Integer(default=30, required=True)
    rounding_minutes = fields.Integer(default=15)
    regular_multiplier = fields.Float(default=1.5, digits=(16, 2), required=True)
    offday_multiplier = fields.Float(default=2.0, digits=(16, 2), required=True)
    hourly_rate = fields.Monetary(currency_field='currency_id', help='Optional rule-level rate. Employee rate takes precedence.')
    currency_id = fields.Many2one(related='company_id.currency_id', readonly=True)

    _sql_constraints = [
        ('minimum_minutes_positive', 'CHECK(minimum_minutes >= 0)', 'Minimum minutes cannot be negative.'),
        ('rounding_minutes_nonnegative', 'CHECK(rounding_minutes >= 0)', 'Rounding minutes cannot be negative.'),
        ('regular_multiplier_positive', 'CHECK(regular_multiplier > 0)', 'Regular multiplier must be greater than zero.'),
        ('offday_multiplier_positive', 'CHECK(offday_multiplier > 0)', 'Off-day multiplier must be greater than zero.'),
    ]
