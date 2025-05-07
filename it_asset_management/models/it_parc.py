# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta

class ITAsset(models.Model):
    _name = 'it.asset'
    _description = 'Équipement Informatique'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nom de l'équipement", required=True, tracking=True)
    image = fields.Binary('Image')
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
    site_id = fields.Many2one('it.site', string='Site', tracking=True)
    purchase_date = fields.Date('Date d\'achat')
    warranty_end_date = fields.Date('Fin de garantie')
    license_end_date = fields.Date('Fin de licence', help="Date d'expiration pour les licences logicielles")
    status = fields.Selection([
        ('nouveau', 'Nouveau'),
        ('utilisé', 'Utilisé'),
        ('en_reparation', 'En réparation'),
    ], string='Statut', default='nouveau', tracking=True)
    description = fields.Text('Description')
    notes = fields.Text('Notes internes')
    contract_id = fields.Many2one('it.contract', string='Contrat associé')
    cost = fields.Float('Coût d\'achat')
    amortization_years = fields.Integer('Durée d\'amortissement (années)', default=3)
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')
    amortized_value = fields.Float('Valeur amortie', compute='_compute_amortized_value', store=True)
    remaining_value = fields.Float('Valeur résiduelle', compute='_compute_amortized_value', store=True)
    product_id = fields.Many2one('product.product', string='Produit', domain=[('type', '=', 'product')])
    last_maintenance_date = fields.Date('Dernière maintenance')
    maintenance_interval = fields.Integer('Intervalle de maintenance (mois)', default=12, help="Intervalle recommandé pour la maintenance préventive")

    @api.depends('cost', 'purchase_date', 'amortization_years')
    def _compute_amortized_value(self):
        today = fields.Date.today()
        for asset in self:
            if asset.cost and asset.purchase_date and asset.amortization_years:
                purchase_date = fields.Date.from_string(asset.purchase_date)
                years_passed = (today - purchase_date).days / 365.25
                annual_amortization = asset.cost / asset.amortization_years
                amortized = min(annual_amortization * years_passed, asset.cost)
                asset.amortized_value = amortized
                asset.remaining_value = asset.cost - amortized
            else:
                asset.amortized_value = 0.0
                asset.remaining_value = asset.cost or 0.0

    @api.model
    def check_warranty_expiration(self):
        today = fields.Date.today()
        assets = self.search([('warranty_end_date', '<=', today)])
        for asset in assets:
            asset.message_post(
                body=f"L'équipement {asset.name} est hors garantie depuis {asset.warranty_end_date}.",
                message_type='notification',
                subtype_id=self.env.ref('mail.mt_note').id
            )
            self.env['mail.activity'].create({
                'res_id': asset.id,
                'res_model_id': self.env['ir.model']._get('it.asset').id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': f"Équipement {asset.name} hors garantie",
                'user_id': asset.client_id.user_id.id or self.env.user.id,
                'date_deadline': today,
            })

    @api.model
    def check_license_expiration(self):
        today = fields.Date.today()
        assets = self.search([('license_end_date', '<=', today), ('category', '=', 'licence')])
        for asset in assets:
            asset.message_post(
                body=f"La licence {asset.name} a expiré le {asset.license_end_date}.",
                message_type='notification',
                subtype_id=self.env.ref('mail.mt_note').id
            )
            self.env['mail.activity'].create({
                'res_id': asset.id,
                'res_model_id': self.env['ir.model']._get('it.asset').id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': f"Licence {asset.name} expirée",
                'user_id': asset.client_id.user_id.id or self.env.user.id,
                'date_deadline': today,
            })

    @api.model
    def check_maintenance_schedule(self):
        today = fields.Date.today()
        assets = self.search([('maintenance_interval', '>', 0)])
        for asset in assets:
            if asset.last_maintenance_date:
                last_maintenance = fields.Date.from_string(asset.last_maintenance_date)
                next_maintenance = last_maintenance + timedelta(days=asset.maintenance_interval * 30)
                if next_maintenance <= today:
                    asset.message_post(
                        body=f"Maintenance préventive recommandée pour l'équipement {asset.name}.",
                        message_type='notification',
                        subtype_id=self.env.ref('mail.mt_note').id
                    )
                    self.env['it.ticket'].create({
                        'name': f"Maintenance préventive - {asset.name}",
                        'client_id': asset.client_id.id,
                        'asset_id': asset.id,
                        'contract_id': asset.contract_id.id,
                        'maintenance_type': 'preventive',
                        'description': f"Maintenance préventive recommandée pour {asset.name}.",
                    })

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