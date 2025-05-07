# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ITSite(models.Model):
    _name = 'it.site'
    _description = 'Site Client'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nom du site', required=True, tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', required=True, domain=[('is_company', '=', True)], tracking=True)
    address = fields.Char('Adresse')
    city = fields.Char('Ville')
    country_id = fields.Many2one('res.country', string='Pays')
    asset_ids = fields.One2many('it.asset', 'site_id', string='Équipements')

class ITAsset(models.Model):
    _inherit = 'it.asset'

    site_id = fields.Many2one('it.site', string='Site', tracking=True)