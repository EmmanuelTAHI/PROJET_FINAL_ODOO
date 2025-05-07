# -*- coding: utf-8 -*-
{
    'name': 'Gestion de Parc Informatique',
    'version': '1.0',
    'category': 'Services/IT',
    'summary': 'Gestion de parc matériel, contrats, incidents et facturation récurrente pour prestataires IT',
    'description': """
Module complet de gestion de parc informatique multi-clients pour prestataire de services IT :
- Suivi du matériel, logiciels et licences
- Gestion des contrats et interventions
- Tickets d'incidents
- Facturation récurrente
- Portail client
""",
    'author': 'TonNom',
    'website': 'https://tonsite.com',

    # Modules nécessaires pour le bon fonctionnement
    'depends': [
        'base',  # Base de données principale
        'sale',  # Pour la gestion des ventes, facturation, etc.
        'account',  # Pour la gestion comptable
        'helpdesk',  # Pour la gestion des tickets d'incidents
        'stock',  # Gestion des stocks et des équipements
        'hr',  # Gestion des ressources humaines si nécessaire
        'website',  # Pour gérer le portail client
        'portal',  # Pour gérer le portail client
    ],

    # Chargement des fichiers nécessaires : sécurité, vues, données, etc.
    'data': [
        'security/security.xml',  # Règles de sécurité et groupes
        'security/ir.model.access.csv',  # Accès aux modèles pour les utilisateurs
        'views/it_asset_views.xml',  # Vues du parc informatique
        'views/it_contract_views.xml',  # Vues des contrats
        'views/it_ticket_views.xml',  # Vues des tickets d'incidents
        'views/it_site_views.xml',  # Vue des différents sites(zones)
        'views/it_client_views.xml',
        'views/it_employe_views.xml',
        'views/portal_templates.xml',
        'reports/it_asset_amortization_report.xml',
        'views/it_menus.xml',  # Menus de l'interface Odoo
        'data/demo.xml',
        'data/cron_jobs.xml',  # Jobs CRON pour les alertes (maintenance, fin de garantie)
        'data/it_sequences.xml',  # Séquences ou identifiants spécifiques pour le module
    ],

    # Fichier de démonstration avec des données de test, à inclure uniquement si nécessaire
    'demo': [
        #'demo/demo.xml',  # Données de démonstration pour tests (facultatif)
    ],

    # Attributs spécifiques au module
    'application': True,  # Le module est une application
    'installable': True,  # Le module peut être installé
    'auto_install': False,  # Le module ne s'installe pas automatiquement
    'license': 'LGPL-3',  # Licence LGPL-3 utilisée par défaut
}
