# -*- coding: utf-8 -*-
{
    'name': "Funding request",

    'summary': """
        Manage Non-Profit Cashflow based on fund requests""",

    'description': """
        Get Income and Expenditure Of a specific fund request.

    """,

    'author': "SodanTec & Vitek",
    'website': "vi-tek.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'funding_request_management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','mail','web','web_digital_sign','account_cancel'],

    # always loaded
    'data': [
    'security/security.xml',
        'security/ir.model.access.csv',
        'views/requests.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/outstanding_requests.xml',
        'views/bills.xml',
        'views/request_report.xml',
        'views/external_layout.xml',
        'views/payment_report.xml',
        'views/sub_payments.xml',
        'views/bulk_receive_wizard.xml',
        'views/request_print_wizard.xml',
        'views/faceform.xml',
        'views/menu_items.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
