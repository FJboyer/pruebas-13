# -*- coding: utf-8 -*-
# from odoo import http


# class 3mitPosDeleteValidation(http.Controller):
#     @http.route('/3mit_pos_delete_validation/3mit_pos_delete_validation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/3mit_pos_delete_validation/3mit_pos_delete_validation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('3mit_pos_delete_validation.listing', {
#             'root': '/3mit_pos_delete_validation/3mit_pos_delete_validation',
#             'objects': http.request.env['3mit_pos_delete_validation.3mit_pos_delete_validation'].search([]),
#         })

#     @http.route('/3mit_pos_delete_validation/3mit_pos_delete_validation/objects/<model("3mit_pos_delete_validation.3mit_pos_delete_validation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('3mit_pos_delete_validation.object', {
#             'object': obj
#         })
