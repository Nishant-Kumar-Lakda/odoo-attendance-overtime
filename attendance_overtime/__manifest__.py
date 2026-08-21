{
    'name': 'Attendance Overtime',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Attendances',
    'summary': 'Calculate, approve, and export attendance overtime',
    'description': '''
Attendance Overtime
===================

Calculate overtime from employee attendances and working schedules, review and
approve overtime, calculate payable amounts, and export payroll-ready CSV data.

Key features:
* Date-range overtime generation from attendances and working schedules.
* Configurable minimum overtime threshold and rounding interval.
* Employee-specific hourly overtime rate with company defaults.
* Regular-day and off-day overtime multipliers.
* Approval workflow: Draft, Submitted, Approved, Rejected.
* Payroll-ready CSV export without requiring a payroll module.
* PDF overtime report.
* Multi-company support.
* No external service, activation key, or vendor lock-in.

The module does not modify Odoo Enterprise validation mechanisms and does not
require Odoo Payroll. Overtime amounts are exported for payroll processing.
''',
    'author': 'Nishant Lakda',
    'price': 59.0,
    'currency': 'EUR',
    'license': 'OPL-1',
    'depends': ['hr_attendance', 'mail'],
    'data': [
        'security/attendance_overtime_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/ir_cron_data.xml',
        'views/attendance_overtime_views.xml',
        'views/attendance_overtime_rule_views.xml',
        'views/attendance_overtime_wizard_views.xml',
        'views/hr_employee_views.xml',
        'views/res_config_settings_views.xml',
        'report/attendance_overtime_report.xml',
    ],
    'images': [
        'static/description/main_screenshot.png',
        'static/description/approval_screenshot.png',
        'static/description/report_screenshot.png',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
