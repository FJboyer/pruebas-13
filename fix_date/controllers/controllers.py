# -*- coding: utf-8 -*-
# from odoo import http


# class FixDate(http.Controller):
#     @http.route('/fix_date/fix_date/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fix_date/fix_date/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fix_date.listing', {
#             'root': '/fix_date/fix_date',
#             'objects': http.request.env['fix_date.fix_date'].search([]),
#         })

#     @http.route('/fix_date/fix_date/objects/<model("fix_date.fix_date"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fix_date.object', {
#             'object': obj
#         })
