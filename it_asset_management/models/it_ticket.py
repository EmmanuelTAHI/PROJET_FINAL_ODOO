# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ITTicket(models.Model):
    _name = 'it.ticket'
    _description = 'Ticket d\'Incident'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Suivi et chatter

    name = fields.Char('Référence du ticket', required=True, default='Nouveau', copy=False, tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', required=True, tracking=True)
    asset_id = fields.Many2one('it.asset', string='Équipement concerné', tracking=True)
    user_id = fields.Many2one('res.users', string='Contact client')
    technician_id = fields.Many2one('hr.employee', string='Technicien assigné')
    description = fields.Text('Description du problème', required=True)
    state = fields.Selection([
        ('new', 'Nouveau'),
        ('in_progress', 'En cours'),
        ('resolved', 'Résolu'),
        ('closed', 'Clôturé'),
    ], string='État', default='new', tracking=True)
    contract_id = fields.Many2one('it.contract', string='Contrat associé')

    resolution_notes = fields.Text('Résolution')
    date_opened = fields.Datetime('Date d\'ouverture', default=fields.Datetime.now)
    date_closed = fields.Datetime('Date de clôture')

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('it.ticket') or 'Nouveau'
        return super(ITTicket, self).create(vals)

    def action_start(self):
        for ticket in self:
            ticket.state = 'in_progress'
            ticket.message_post(body="Ticket pris en charge.")

    def action_resolve(self):
        for ticket in self:
            ticket.state = 'resolved'
            ticket.date_closed = fields.Datetime.now()
            ticket.message_post(body="Ticket résolu.")

    def action_close(self):
        for ticket in self:
            ticket.state = 'closed'
            ticket.message_post(body="Ticket clôturé.")
