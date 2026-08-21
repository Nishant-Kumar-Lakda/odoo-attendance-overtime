import base64
import csv
import io
from datetime import datetime, time, timedelta

import pytz

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class AttendanceOvertime(models.Model):
    _name = 'attendance.overtime'
    _description = 'Attendance Overtime'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, employee_id'

    name = fields.Char(required=True, copy=False, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', required=True, index=True, ondelete='cascade')
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', required=True, index=True, default=lambda self: self.env.company, ondelete='cascade')
    date = fields.Date(required=True, index=True)
    expected_hours = fields.Float(digits=(16, 2), readonly=True)
    worked_hours = fields.Float(digits=(16, 2), readonly=True)
    overtime_hours = fields.Float(digits=(16, 2), readonly=True)
    approved_overtime_hours = fields.Float(digits=(16, 2), tracking=True)
    overtime_type = fields.Selection([('regular', 'Regular Day'), ('offday', 'Off Day')], required=True, default='regular', readonly=True)
    hourly_rate = fields.Monetary(currency_field='currency_id', readonly=True)
    multiplier = fields.Float(digits=(16, 2), readonly=True)
    overtime_amount = fields.Monetary(currency_field='currency_id', readonly=True)
    currency_id = fields.Many2one(related='company_id.currency_id', readonly=True)
    first_check_in = fields.Datetime(readonly=True)
    last_check_out = fields.Datetime(readonly=True)
    attendance_ids = fields.Many2many('hr.attendance', string='Source Attendances', readonly=True)
    rule_id = fields.Many2one('attendance.overtime.rule', readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='draft', required=True, tracking=True, index=True)
    rejection_reason = fields.Text(tracking=True)
    export_reference = fields.Char(readonly=True, copy=False)

    _sql_constraints = [
        ('employee_date_unique', 'unique(employee_id, date)', 'Only one overtime record is allowed per employee and date.'),
        ('approved_hours_nonnegative', 'CHECK(approved_overtime_hours >= 0)', 'Approved overtime hours cannot be negative.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name') in (False, _('New'), 'New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('attendance.overtime') or _('New')
            vals.setdefault('company_id', self.env.company.id)
        records = super().create(vals_list)
        records._recompute_amount()
        return records

    def write(self, vals):
        if 'approved_overtime_hours' in vals:
            for record in self:
                if record.state in ('approved', 'rejected') and not self.env.user.has_group('attendance_overtime.group_attendance_overtime_manager'):
                    raise UserError(_('Only overtime managers can modify approved or rejected records.'))
        result = super().write(vals)
        if any(key in vals for key in ('approved_overtime_hours', 'hourly_rate', 'multiplier')):
            self._recompute_amount()
        return result

    @api.constrains('approved_overtime_hours', 'overtime_hours')
    def _check_approved_hours(self):
        for record in self:
            if record.approved_overtime_hours > record.overtime_hours + 1e-6:
                raise ValidationError(_('Approved overtime cannot exceed calculated overtime.'))

    def _recompute_amount(self):
        for record in self:
            record.overtime_amount = record.approved_overtime_hours * record.hourly_rate * record.multiplier

    def action_submit(self):
        for record in self:
            if record.overtime_hours <= 0:
                raise UserError(_('Only records with overtime can be submitted.'))
            if record.approved_overtime_hours <= 0:
                record.approved_overtime_hours = record.overtime_hours
            record.state = 'submitted'
        return True

    def action_approve(self):
        self._check_manager()
        for record in self:
            if record.state != 'submitted':
                raise UserError(_('Only submitted overtime can be approved.'))
            record.state = 'approved'
        return True

    def action_reject(self):
        self._check_manager()
        return {'type': 'ir.actions.act_window', 'name': _('Reject Overtime'), 'res_model': 'attendance.overtime.reject.wizard', 'view_mode': 'form', 'target': 'new', 'context': {'active_ids': self.ids}}

    def action_reset_to_draft(self):
        self._check_manager()
        self.write({'state': 'draft', 'rejection_reason': False})
        return True

    def _check_manager(self):
        if not self.env.user.has_group('attendance_overtime.group_attendance_overtime_manager'):
            raise UserError(_('Only overtime managers can perform this action.'))

    @api.model
    def _date_bounds_utc(self, employee, date_value):
        tz = pytz.timezone(employee.tz or self.env.company.tz or 'UTC')
        start_local = tz.localize(datetime.combine(date_value, time.min))
        end_local = start_local + timedelta(days=1)
        return start_local.astimezone(pytz.UTC).replace(tzinfo=None), end_local.astimezone(pytz.UTC).replace(tzinfo=None)

    @api.model
    def _expected_hours(self, employee, start_utc, end_utc):
        calendar = employee.resource_calendar_id or employee.company_id.resource_calendar_id
        if not calendar:
            return 0.0
        try:
            return calendar.get_work_hours_count(start_utc, end_utc, compute_leaves=True, employee=employee)
        except TypeError:
            return calendar.get_work_hours_count(start_utc, end_utc, compute_leaves=True)

    @api.model
    def _employee_rate(self, employee, rule):
        if employee.overtime_hourly_rate:
            return employee.overtime_hourly_rate
        if rule and rule.hourly_rate:
            return rule.hourly_rate
        return employee.company_id.attendance_overtime_hourly_rate

    @api.model
    def generate_for_employee(self, employee, date_value, rule=False):
        rule = rule or self.env['attendance.overtime.rule'].search([('active', '=', True), ('company_id', '=', employee.company_id.id)], order='sequence,id', limit=1)
        company = employee.company_id
        minimum_minutes = rule.minimum_minutes if rule else company.attendance_overtime_min_minutes
        rounding_minutes = rule.rounding_minutes if rule else company.attendance_overtime_rounding_minutes
        regular_multiplier = rule.regular_multiplier if rule else company.attendance_overtime_multiplier
        offday_multiplier = rule.offday_multiplier if rule else company.attendance_overtime_offday_multiplier
        start_utc, end_utc = self._date_bounds_utc(employee, date_value)
        attendances = self.env['hr.attendance'].search([('employee_id', '=', employee.id), ('check_in', '<', end_utc), '|', ('check_out', '=', False), ('check_out', '>', start_utc)])
        worked_hours = 0.0
        first_check_in = False
        last_check_out = False
        attendance_ids = []
        for attendance in attendances:
            check_in = max(attendance.check_in, start_utc)
            check_out = min(attendance.check_out or fields.Datetime.now(), end_utc)
            if check_out <= check_in:
                continue
            worked_hours += (check_out - check_in).total_seconds() / 3600.0
            attendance_ids.append(attendance.id)
            first_check_in = min(first_check_in, attendance.check_in) if first_check_in else attendance.check_in
            last_check_out = max(last_check_out, attendance.check_out or check_out) if last_check_out else (attendance.check_out or check_out)
        expected_hours = self._expected_hours(employee, start_utc, end_utc)
        raw_overtime = max(worked_hours - expected_hours, 0.0)
        if raw_overtime * 60 < minimum_minutes:
            overtime_hours = 0.0
        elif rounding_minutes:
            minutes = int(raw_overtime * 60)
            overtime_hours = (minutes // rounding_minutes) * rounding_minutes / 60.0
        else:
            overtime_hours = raw_overtime
        overtime_type = 'offday' if expected_hours <= 1e-6 else 'regular'
        multiplier = offday_multiplier if overtime_type == 'offday' else regular_multiplier
        rate = self._employee_rate(employee, rule)
        existing = self.search([('employee_id', '=', employee.id), ('date', '=', date_value)], limit=1)
        vals = {'employee_id': employee.id, 'date': date_value, 'company_id': company.id, 'expected_hours': round(expected_hours, 2), 'worked_hours': round(worked_hours, 2), 'overtime_hours': round(overtime_hours, 2), 'approved_overtime_hours': round(overtime_hours, 2), 'overtime_type': overtime_type, 'hourly_rate': rate, 'multiplier': multiplier, 'first_check_in': first_check_in, 'last_check_out': last_check_out, 'attendance_ids': [Command.set(attendance_ids)], 'rule_id': rule.id if rule else False}
        if existing and existing.state in ('draft', 'rejected'):
            existing.write(vals)
            existing._recompute_amount()
            return existing
        if existing:
            return existing
        record = self.create(vals)
        record._recompute_amount()
        return record

    @api.model
    def cron_generate_previous_day(self):
        yesterday = fields.Date.context_today(self) - timedelta(days=1)
        for employee in self.env['hr.employee'].search([('active', '=', True)]):
            self.generate_for_employee(employee, yesterday)
        return True

    def action_export_payroll_csv(self):
        if not self:
            raise UserError(_('Select at least one overtime record.'))
        self._check_manager()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Reference', 'Employee', 'Badge ID', 'Department', 'Date', 'Type', 'Expected Hours', 'Worked Hours', 'Calculated Overtime', 'Approved Overtime', 'Hourly Rate', 'Multiplier', 'Overtime Amount', 'Status'])
        for record in self:
            writer.writerow([record.name, record.employee_id.name, record.employee_id.barcode or '', record.department_id.name or '', record.date.isoformat(), dict(record._fields['overtime_type'].selection).get(record.overtime_type), record.expected_hours, record.worked_hours, record.overtime_hours, record.approved_overtime_hours, record.hourly_rate, record.multiplier, record.overtime_amount, dict(record._fields['state'].selection).get(record.state)])
        data = base64.b64encode(output.getvalue().encode('utf-8-sig'))
        attachment = self.env['ir.attachment'].create({'name': 'attendance_overtime_payroll.csv', 'type': 'binary', 'datas': data, 'mimetype': 'text/csv', 'res_model': self._name, 'res_id': self[0].id})
        self.write({'export_reference': attachment.name})
        return {'type': 'ir.actions.act_url', 'url': f'/web/content/{attachment.id}?download=true', 'target': 'self'}
