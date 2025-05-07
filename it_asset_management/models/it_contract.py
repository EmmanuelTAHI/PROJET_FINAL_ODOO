# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class ITContract(models.Model):
    _name = 'it.contract'
    _description = 'Contrat de Service'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Référence du contrat', required=True, tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True)
    start_date = fields.Date('Date de début', required=True)
    end_date = fields.Date('Date de fin', required=True)
    frequency = fields.Selection([
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
    ], string='Fréquence de facturation', required=True, default='monthly', tracking=True)
    price = fields.Integer('Prix récurrent', required=True)
    account_id = fields.Many2one('account.account', string='Compte comptable', domain=[('deprecated', '=', False)])
    service_description = fields.Text('Description des services')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('expired', 'Expiré'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True)

    asset_ids = fields.One2many('it.asset', 'contract_id', string='Équipements inclus')
    invoice_ids = fields.One2many('account.move', 'contract_id', string='Factures')
    next_invoice_date = fields.Date('Prochaine facturation', compute='_compute_next_invoice_date', store=True)

    @api.depends('start_date', 'frequency')
    def _compute_next_invoice_date(self):
        for contract in self:
            if contract.start_date:
                if contract.frequency == 'monthly':
                    contract.next_invoice_date = contract.start_date + relativedelta(months=1)
                elif contract.frequency == 'quarterly':
                    contract.next_invoice_date = contract.start_date + relativedelta(months=3)
                elif contract.frequency == 'yearly':
                    contract.next_invoice_date = contract.start_date + relativedelta(years=1)
            else:
                contract.next_invoice_date = False

    def _check_contract_expiry(self):
        today = fields.Date.today()
        contracts = self.search([('end_date', '<=', today), ('state', '=', 'active')])
        for contract in contracts:
            contract.state = 'expired'
            contract.message_post(body="Contrat expiré.")

    def action_activate(self):
        for contract in self:
            contract.state = 'active'
            contract.message_post(body="Contrat activé.")

    def action_cancel(self):
        for contract in self:
            contract.state = 'cancelled'
            contract.message_post(body="Contrat annulé.")

    def generate_recurring_invoices(self):
        today = fields.Date.today()
        contracts = self.search([('state', '=', 'active'), ('next_invoice_date', '<=', today)])
        for contract in contracts:
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': contract.client_id.id,
                'invoice_date': today,
                'contract_id': contract.id,
                'invoice_line_ids': [(0, 0, {
                    'name': f'Abonnement {contract.name}',
                    'quantity': 1,
                    'price_unit': contract.price,
                    'account_id': contract.account_id.id if contract.account_id else False,
                })],
            }
            invoice = self.env['account.move'].create(invoice_vals)
            invoice.action_post()
            contract.message_post(body=f"Facture {invoice.name} générée.")

            if contract.frequency == 'monthly':
                contract.next_invoice_date += relativedelta(months=1)
            elif contract.frequency == 'quarterly':
                contract.next_invoice_date += relativedelta(months=3)
            elif contract.frequency == 'yearly':
                contract.next_invoice_date += relativedelta(years=1)

            if contract.next_invoice_date > contract.end_date:
                contract.state = 'expired'
                contract.message_post(body="Contrat expiré.")

class AccountMove(models.Model):
    _inherit = 'account.move'

    contract_id = fields.Many2one('it.contract', string='Contrat associé')