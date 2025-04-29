# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ITAsset(models.Model):
    _name = 'it.asset'
    _description = 'Équipement Informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nom de l'équipement", required=True, tracking=True)
    image = fields.Binary('Image')
    asset_tag = fields.Char("Tag d'équipement")
    serial_number = fields.Char('Numéro de série')
    category = fields.Selection([
        ('ordinateur', 'Ordinateur'),
        ('imprimante', 'Imprimante'),
        ('routeur', 'Routeur'),
        ('licence', 'Licence Logicielle'),
        ('autre', 'Autre'),
    ], string='Catégorie', required=True, tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', domain=[('is_company', '=', True)], tracking=True)
    assigned_user_id = fields.Many2one(
        'res.partner',
        string='Utilisateur Assigné',
        domain="[('parent_id', '=', client_id)]",
        tracking=True
    )
    location = fields.Char('Localisation')
    purchase_date = fields.Date('Date d\'achat')
    warranty_end_date = fields.Date('Fin de garantie')
    state = fields.Selection([
        ('en_service', 'En Service'),
        ('en_maintenance', 'En Maintenance'),
        ('retour', 'À Retourner'),
        ('retire', 'Retiré'),
    ], string='État', default='en_service', tracking=True)
    status = fields.Selection([
        ('nouveau', 'Nouveau'),
        ('utilisé', 'Utilisé'),
        ('en_reparation', 'En réparation'),
        ('perdu', 'Perdu'),
    ], string='Statut', default='nouveau', tracking=True)
    description = fields.Text('Description')
    notes = fields.Text('Notes internes')
    contract_id = fields.Many2one('it.contract', string='Contrat associé')
    cost = fields.Float('Coût d\'achat')
    amortization_years = fields.Integer('Durée d\'amortissement (années)', default=3)
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')

    @api.model
    def check_warranty_expiration(self):
        today = fields.Date.today()
        assets = self.search([('warranty_end_date', '<=', today), ('state', '=', 'en_service')])
        for asset in assets:
            asset.message_post(
                body=f"L'équipement {asset.name} est hors garantie depuis {asset.warranty_end_date}."
            )

class ResPartner(models.Model):
    _inherit = 'res.partner'

    equipment_count = fields.Integer(
        string='Nombre d\'équipements',
        compute='_compute_equipment_count',
        store=False
    )
    assigned_equipment_count = fields.Integer(
        string='Équipements Assignés',
        compute='_compute_assigned_equipment_count',
        store=False
    )

    @api.depends('is_company')
    def _compute_equipment_count(self):
        for partner in self:
            if partner.is_company:
                equipment_count = self.env['it.asset'].search_count([('client_id', '=', partner.id)])
                partner.equipment_count = equipment_count
            else:
                partner.equipment_count = 0

    def _compute_assigned_equipment_count(self):
        for partner in self:
            if not partner.is_company and partner.parent_id:
                equipment_count = self.env['it.asset'].search_count([('assigned_user_id', '=', partner.id)])
                partner.assigned_equipment_count = equipment_count
            else:
                partner.assigned_equipment_count = 0