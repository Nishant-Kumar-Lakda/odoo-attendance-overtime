# Odoo Apps submission checklist

Prepared for Odoo 19 and intended for marketplace review.

## Manifest

- App name: `Attendance Overtime`
- Version: `19.0.1.0.0`
- License: `OPL-1`
- Dependencies: `hr_attendance`, `mail`
- Price: EUR 59
- No activation server, telemetry, external API, executable download, or vendor lock-in.

## Functionality

- Attendance-based daily overtime calculation.
- Working-calendar comparison.
- Minimum threshold and rounding.
- Regular/off-day multipliers.
- Employee/rule/company rate fallback.
- Draft, Submitted, Approved, Rejected workflow.
- PDF report.
- Payroll-ready CSV export.
- Daily scheduled generation.
- Multi-company support.

## Final checks before publication

1. Install on a clean Odoo 19 database.
2. Run functional tests with real attendance and resource-calendar data.
3. Verify all security roles and multi-company behavior.
4. Verify screenshots against the final installed UI.
5. Run the Odoo Apps Store repository scan.
6. Confirm the marketplace price is not higher than the price offered elsewhere.
7. Replace any placeholder support/contact information before publishing.

The repository is source-complete for the text-based module files. Binary marketplace screenshots/icon remain in the release ZIP and should be committed separately before marketplace submission.
