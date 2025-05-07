# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class ITPortal(http.Controller):
    @http.route(['/my/assets'], type='http', auth='user', website=True)
    def portal_assets(self):
        partner = request.env.user.partner_id
        assets = request.env['it.asset'].search([('client_id', '=', partner.id)])
        return request.render('it_asset_management.portal_assets_list', {'assets': assets})

    @http.route(['/my/contracts'], type='http', auth='user', website=True)
    def portal_contracts(self):
        partner = request.env.user.partner_id
        contracts = request.env['it.contract'].search([('client_id', '=', partner.id)])
        return request.render('it_asset_management.portal_contracts_list', {'contracts': contracts})

    @http.route(['/my/tickets', '/my/tickets/<int:ticket_id>'], type='http', auth='user', website=True)
    def portal_tickets(self, ticket_id=None):
        partner = request.env.user.partner_id
        tickets = request.env['it.ticket'].search([('client_id', '=', partner.id)])
        return request.render('it_asset_management.portal_tickets_list', {'tickets': tickets})

    @http.route(['/my/tickets/new'], type='http', auth='user', website=True)
    def portal_new_ticket(self):
        partner = request.env.user.partner_id
        assets = request.env['it.asset'].search([('client_id', '=', partner.id)])
        return request.render('it_asset_management.portal_new_ticket', {'assets': assets})

    @http.route(['/my/tickets/submit'], type='http', auth='user', methods=['POST'], website=True)
    def portal_submit_ticket(self, **post):
        partner = request.env.user.partner_id
        values = {
            'client_id': partner.id,
            'asset_id': int(post.get('asset_id')),
            'description': post.get('description'),
            'user_id': request.env.user.id,
        }
        ticket = request.env['it.ticket'].sudo().create(values)
        return request.redirect('/my/tickets')