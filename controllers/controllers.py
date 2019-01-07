# -*- coding: utf-8 -*-
from odoo import http

# class FundingRequestManagement(http.Controller):
#     @http.route('/funding_request_management/funding_request_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/funding_request_management/funding_request_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('funding_request_management.listing', {
#             'root': '/funding_request_management/funding_request_management',
#             'objects': http.request.env['funding_request_management.funding_request_management'].search([]),
#         })

#     @http.route('/funding_request_management/funding_request_management/objects/<model("funding_request_management.funding_request_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('funding_request_management.object', {
#             'object': obj
#         })