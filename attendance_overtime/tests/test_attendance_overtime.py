from odoo.tests import TransactionCase


class TestAttendanceOvertime(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.employee = cls.env['hr.employee'].create({'name': 'Overtime Test Employee', 'company_id': cls.company.id, 'overtime_hourly_rate': 100.0})

    def test_create_and_submit_overtime(self):
        record = self.env['attendance.overtime'].create({'employee_id': self.employee.id, 'date': '2026-08-20', 'company_id': self.company.id, 'expected_hours': 8.0, 'worked_hours': 10.0, 'overtime_hours': 2.0, 'approved_overtime_hours': 2.0, 'overtime_type': 'regular', 'hourly_rate': 100.0, 'multiplier': 1.5})
        self.assertEqual(record.name[:3], 'OT/')
        self.assertAlmostEqual(record.overtime_amount, 300.0)
        record.action_submit()
        self.assertEqual(record.state, 'submitted')

    def test_approved_hours_cannot_exceed_calculated(self):
        with self.assertRaises(Exception):
            self.env['attendance.overtime'].create({'employee_id': self.employee.id, 'date': '2026-08-21', 'company_id': self.company.id, 'expected_hours': 8.0, 'worked_hours': 9.0, 'overtime_hours': 1.0, 'approved_overtime_hours': 2.0, 'overtime_type': 'regular', 'hourly_rate': 100.0, 'multiplier': 1.5})
