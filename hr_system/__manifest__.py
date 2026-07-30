{
    'name': 'HR System',
    'author': 'Odoo Abdelsalam',
    'version': '17.0.0.1.0',
    'depends': [],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/main_system_menu.xml',
        'views/employees_view.xml',
        'views/departments_view.xml',
        'views/roles_view.xml',
        'views/attendance_logs.xml',
        'views/payroll_view.xml',
    ],
    'application': True
}
