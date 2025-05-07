# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Pour compter les équipements attribués à un employé
    assigned_equipment_count = fields.Integer(
        string="Équipements assignés",
        compute='_compute_assigned_equipment_count'
    )

    # Pour compter les équipements liés à un client
    equipment_count = fields.Integer(
        string="Équipements du client",
        compute='_compute_equipment_count'
    )

    # Pour qu’un client voie ses employés associés
    employee_ids = fields.One2many(
        'res.partner', 'parent_id',
        string="Employés"
    )

    def _compute_assigned_equipment_count(self):
        for rec in self:
            rec.assigned_equipment_count = self.env['it.asset'].search_count([
                ('employee_id', '=', rec.id)
            ])

    def _compute_equipment_count(self):
        for rec in self:
            rec.equipment_count = self.env['it.asset'].search_count([
                ('client_id', '=', rec.id)
            ])
