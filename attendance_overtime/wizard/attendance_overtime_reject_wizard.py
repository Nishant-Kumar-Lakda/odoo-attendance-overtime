from odoo import fields, models


class AttendanceOvertimeRejectWizard(models.TransientModel):
    _name = 'attendance.overtime.reject.wizard'
    _description = 'Reject Attendance Overtime'

    reason = fields.Text(required=True)

    def action_reject(self):
        records = self.env['attendance.overtime'].browse(self.env.context.get('active_ids', [])).exists()
        records._check_manager()
        records.write({'state': 'rejected', 'rejection_reason': self.reason})
        return {'type': 'ir.actions.act_window_close'}
