from odoo import http
from odoo.http import request


class ItAssetManagementPortal(http.Controller):

    # Route pour afficher les tickets d'incidents d'un client
    @http.route('/my/tickets', auth='user', website=True)
    def tickets(self, **kw):
        tickets = request.env['it.ticket'].search([('client_id', '=', request.env.user.partner_id.id)])
        return request.render('it_asset_management.portal_tickets', {
            'tickets': tickets
        })

    # Route pour afficher le parc informatique du client
    @http.route('/my/it_assets', auth='user', website=True)
    def it_assets(self, **kw):
        assets = request.env['it.asset'].search([('client_id', '=', request.env.user.partner_id.id)])
        return request.render('it_asset_management.portal_it_assets', {
            'assets': assets
        })

    # Route pour afficher les contrats du client
    @http.route('/my/contracts', auth='user', website=True)
    def contracts(self, **kw):
        contracts = request.env['it.contract'].search([('client_id', '=', request.env.user.partner_id.id)])
        return request.render('it_asset_management.portal_contracts', {
            'contracts': contracts
        })
