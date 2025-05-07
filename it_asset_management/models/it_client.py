# -*- coding: utf-8 -*-
from odoo import models

class ItClient(models.Model):
    _inherit = 'res.partner'
    # Pas de nouveaux champs, mais on peut restreindre ou surcharger des méthodes ici si nécessaire.
