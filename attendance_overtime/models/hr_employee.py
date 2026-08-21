from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    overtime_hourly_rate = fields.Monetary(
        string='Overtime Hourly Rate',
        currency_field='currency_id',
        groups='hr.group_hr_user',
        help='Overrides the company default hourly overtime rate for this employee.',
    )
