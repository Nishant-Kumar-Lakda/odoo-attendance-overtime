# Attendance Overtime for Odoo 19

Attendance Overtime calculates daily overtime from Odoo Attendances and employee working schedules. It provides an approval and payroll-export layer without requiring Odoo Payroll.

## Features

- Generate overtime for a date range and selected employees.
- Use employee working schedules to determine expected hours.
- Detect off-day work when scheduled hours are zero.
- Minimum overtime threshold and rounding interval.
- Employee, rule, and company hourly-rate fallback.
- Regular and off-day multipliers.
- Draft, Submitted, Approved, and Rejected workflow.
- PDF report.
- Payroll-ready CSV export.
- Daily scheduled generation for the previous day.
- Multi-company support.

## Dependencies

- `hr_attendance`
- `mail`

No external service, API key, activation server, executable download, or telemetry is required.

## Installation

Copy the `attendance_overtime` directory into an Odoo addons path, update the Apps list, install **Attendance Overtime**, configure the rules, and set employee hourly rates where required.

## Calculation

Daily overtime is calculated as:

`max(worked hours - scheduled hours, 0)`

The configured minimum threshold and rounding interval are then applied. Approved overtime amount is:

`approved overtime hours × hourly rate × multiplier`

The module exports approved overtime as CSV for payroll processing instead of writing directly to payroll models.
