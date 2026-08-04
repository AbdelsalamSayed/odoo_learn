{
    "name": "HR System",
    "author": "Odoo Abdelsalam",
    "version": "17.0.0.1.0",
    "depends": [],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/main_system_menu.xml",
        "views/employees_view.xml",
        "views/employee_loan.xml",
        "views/departments_view.xml",
        "views/attendance_logs.xml",
        "views/employee_attendance.xml",
        "views/ir_cron_data.xml",
        "views/payroll_view.xml",
        "views/res_user_view.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'hr_system/static/src/ls/attendance_time.js',
        ],
    },
    "application": True,
}
