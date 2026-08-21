from datetime import timedelta

from odoo import fields, models


class AttendanceOvertimeGenerateWizard(models.TransientModel):
    _name = 'attendance.overtime.generate.wizard'
    _description = 'Generate Attendance Overtime'

    date_from = fields.Date(required=True, default=lambda self: fields.Date.context_today(self) - timedelta(days=7))
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    def action_generate(self):
        employees = self.employee_ids or self.env['hr.employee'].search([('company_id', '=', self.company_id.id), ('active', '=', True)])
        date_value = self.date_from
        overtime_model = self.env['attendance.overtime']
        while date_value <= self.date_to:
            for employee in employees.filtered(lambda e: e.company_id == self.company_id):
                overtime_model.generate_for_employee(employee, date_value)
            date_value += timedelta(days=1)
        return {'type': 'ir.actions.act_window', 'name': 'Attendance Overtime', 'res_model': 'attendance.overtime', 'view_mode': 'list,kanban,form,pivot,graph', 'domain': [('date', '>=', self.date_from), ('date', '<=', self.date_to)]}
