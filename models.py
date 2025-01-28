from odoo import models, fields, api # type: ignore warning

class Complaint(models.Model):
    _name = 'complaint.management'
    _description = 'Gestion interne des réclamations'

    x_is_dashboard = fields.Boolean(string='dashboard',default=False)

    x_agence_id = fields.Many2one(
        "res.company",
        string="Agence",
        default=lambda self: self.env.user.company_id,
    )

    x_objet = fields.Char(string='Objet', required=True)
    x_description = fields.Text(string='Description')
    x_categorie = fields.Selection([
        ('Technique', 'Technique'),
        ('Commerciale', 'Commerciale')
    ],string='Catégorie')
    x_date_reception = fields.Datetime(string='Date de réception', default=fields.Datetime.now)
    x_etat_traitement = fields.Selection([
        ('Nouvelle', 'Nouvelle'),
        ('En cours', 'En cours'),
        ('Résolue', 'Résolue'),
        ('Archivée', 'Archivée')
    ], string='Statut', default='Nouvelle')
    x_urgence = fields.Boolean(string='Urgente', default=False)
    x_origine = fields.Selection([
        ('Citoyen', 'Citoyen'),
        ('Entreprise', 'Entreprise'),
        ('Cellule de veille', 'Cellule de veille'),
    ], string='Origine')
    x_reclamant = fields.Many2one('res.partner', string='Réclamant')
    x_assignee_a = fields.Many2many(
        'res.users',
        'complaint_assignee_a_rel',  # Nom de la table intermédiaire
        'complaint_id',  # Colonne pour l'ID de réclamation
        'user_id',  # Colonne pour l'ID utilisateur
        string="Assigné à", 
        #default=lambda self: self.env.user
    )
    x_date_resolution = fields.Datetime(string='Date de résolution')
    x_comments = fields.Text(string='Commentaires')    #si necessaire
    x_attachements = fields.Many2many(
        "ir.attachment",
        string="Pièces jointes",
        help="Ajoutez plusieurs pièces jointes",
    )
    x_traite_par = fields.Many2many(
    'res.users',
    'complaint_traite_par_rel',  # Nom de la table intermédiaire
    'complaint_id',  # Colonne pour l'ID de réclamation
    'user_id',  # Colonne pour l'ID utilisateur
    string='Traité par'
    )
    x_chef= fields.Many2one('res.users', string='Chef d\'équipe technique')
    x_decision= fields.Text(string="Décision")
    x_gravite= fields.Selection([
        ('Faible', 'Faible'),
        ('Moyenne', 'Moyenne'),
        ('Elevée', 'Elevée'),
    ], string='Gravité')

    # Historique des actions
    action_history = fields.One2many('complaint.action', 'complaint_id', string='Historique des actions')

    # Historique des appels
    call_history = fields.One2many('complaint.call', 'x_complaint_id', string='Historique des appels')    
    
    x_feedback_note = fields.Integer(string="Note de satisfaction (/5)")
    x_feedback_description = fields.Text(string="Commentaires")

    total_complaints = fields.Integer(string="Total des reclamations", compute="_compute_total_complaints")
    average_resolution_delay = fields.Float(string="Délai moyen de traitement (jours)", compute="_compute_average_resolution_delay")
    average_feedback_note = fields.Float(string="Moyenne des notes de feedback", compute="_compute_average_feedback_note")
    technical_complaints = fields.Integer(string="Réclamations Techniques", compute="_compute_complaint_types")
    commercial_complaints = fields.Integer(string="Réclamations Commerciales", compute="_compute_complaint_types")
    citoyen_complaints = fields.Integer(string="Réclamations Citoyen", compute="_compute_complaint_origins")
    entreprise_complaints = fields.Integer(string="Réclamations Entreprise", compute="_compute_complaint_origins")
    cellule_veille_complaints = fields.Integer(string="Réclamations Cellule de Veille", compute="_compute_complaint_origins")
    nouvelle_complaints = fields.Integer(string="Réclamations Nouvelles", compute="_compute_complaint_status")
    en_cours_complaints = fields.Integer(string="Réclamations En Cours", compute="_compute_complaint_status")
    resolue_complaints = fields.Integer(string="Réclamations Résolues", compute="_compute_complaint_status")
    archivee_complaints = fields.Integer(string="Réclamations Archivées", compute="_compute_complaint_status")
    
    @api.depends()
    def _compute_total_complaints(self):
        for record in self:
            record.total_complaints = self.env['complaint.management'].sudo().search_count([]) - 1

    @api.depends()
    def _compute_average_resolution_delay(self):
        resolved_complaints = self.env['complaint.management'].sudo().search([
            ('x_date_resolution', '!=', False),
            ('x_date_reception', '!=', False),
            ('x_is_dashboard','=',False)
        ])
        delays = [
            (fields.Date.from_string(complaint.x_date_resolution) - fields.Date.from_string(complaint.x_date_reception)).days
            for complaint in resolved_complaints
        ]
        self.average_resolution_delay = sum(delays) / len(delays) if delays else 0.0

    @api.depends()
    def _compute_average_feedback_note(self):
        feedback_notes = self.env['complaint.management'].sudo().search([('x_feedback_note', '!=', None)]).mapped('x_feedback_note')
        self.average_feedback_note = sum(feedback_notes) / len(feedback_notes) if feedback_notes else 0.0   
    
    @api.depends()
    def _compute_complaint_types(self):
        # Récupérer toutes les réclamations valides (modèle dépendant)
        all_complaints = self.env['complaint.management'].sudo().search([('x_categorie', '!=', None)])

        for record in self:
            # Filtrer les réclamations techniques et commerciales
            technical_complaints = all_complaints.filtered(lambda c: c.x_categorie == 'Technique')
            commercial_complaints = all_complaints.filtered(lambda c: c.x_categorie == 'Commerciale')

            # Calculer les totaux pour cet enregistrement
            record.technical_complaints = len(technical_complaints)
            record.commercial_complaints = len(commercial_complaints)

    @api.depends()
    def _compute_complaint_origins(self):
        # Récupérer toutes les réclamations valides
        all_complaints = self.env['complaint.management'].sudo().search([('x_origine', '!=', None)])

        for record in self:
            # Filtrer par origine
            citoyen_complaints = all_complaints.filtered(lambda c: c.x_origine == 'Citoyen')
            entreprise_complaints = all_complaints.filtered(lambda c: c.x_origine == 'Entreprise')
            cellule_veille_complaints = all_complaints.filtered(lambda c: c.x_origine == 'Cellule de veille')

            # Assignation des valeurs
            record.citoyen_complaints = len(citoyen_complaints)
            record.entreprise_complaints = len(entreprise_complaints)
            record.cellule_veille_complaints = len(cellule_veille_complaints)       

    @api.depends()
    def _compute_complaint_status(self):
        # Récupérer toutes les réclamations valides
        all_complaints = self.env['complaint.management'].sudo().search([('x_etat_traitement', '!=', None)])

        for record in self:
            # Filtrer par statut
            nouvelle_complaints = all_complaints.filtered(lambda c: c.x_etat_traitement == 'Nouvelle')
            en_cours_complaints = all_complaints.filtered(lambda c: c.x_etat_traitement == 'En cours')
            resolue_complaints = all_complaints.filtered(lambda c: c.x_etat_traitement == 'Résolue')
            archivee_complaints = all_complaints.filtered(lambda c: c.x_etat_traitement == 'Archivée')

            # Assignation des valeurs , -1 pour le dashboard
            record.nouvelle_complaints = len(nouvelle_complaints) - 1 
            record.en_cours_complaints = len(en_cours_complaints)
            record.resolue_complaints = len(resolue_complaints)
            record.archivee_complaints = len(archivee_complaints)         

    
    @api.model
    def create(self, vals):
        # Récupérer l'utilisateur courant
        user = self.env.user

        # Vérifier si l'utilisateur appartient au groupe "group_cm_agent_clientele"
        if user.has_group('complaintManagement.group_cm_agent_clientele'):
            # Ajouter l'utilisateur dans x_assignee_a s'il n'est pas déjà inclus
            if 'x_assignee_a' in vals:
                vals['x_assignee_a'].append((4, user.id))
            else:
                vals['x_assignee_a'] = [(4, user.id)]

        # Créer l'enregistrement
        record = super(Complaint, self).create(vals)

        # Définir l'état initial à "nouvelle"
        record.x_etat_traitement = 'Nouvelle'

        return record
    

    def write(self, vals):
        res = super(Complaint, self).write(vals)

        # Vérification et mise à jour de l'état de traitement
        for record in self:
            if 'x_traite_par' in vals and vals['x_traite_par']:
                record.x_etat_traitement = 'En cours'
            if 'x_date_resolution' in vals and vals['x_date_resolution']:
                record.x_etat_traitement = 'Résolue'
            if 'x_feedback_note' in vals and vals ['x_feedback_note']:
                record.x_etat_traitement = 'Archivée'

        return res

class ComplaintAction(models.Model):
    _name = 'complaint.action'
    _description = 'Actions liées aux réclamations'

    complaint_id = fields.Many2one('complaint.management', string='Réclamation associée', required=True)
    x_action_date = fields.Datetime(string='Date de l\'action', default=fields.Datetime.now)
    x_action_note = fields.Text(string='Description de l\'action')
    
    

class ComplaintCall(models.Model):
    _name='complaint.call'
    _description='Appels téléphoniques'

    x_complaint_id = fields.Many2one('complaint.management', string='Réclamation associée', required=True)
    x_call_date = fields.Datetime(string='Date de l\'appel', default=fields.Datetime.now)
    x_call_object = fields.Char(string='Objet de l\'appel', required=True)
    x_call_description = fields.Text(string='Description de l\'appel')  



class ComplaintDashboard(models.Model):
    _name = 'complaint.dashboard'
    _description = 'Tableau de bord des réclamations'

    total_complaints = fields.Integer(string="Total des réclamations", compute="_compute_dashboard_values")
    average_resolution_delay = fields.Float(string="Délai moyen de traitement", compute="_compute_dashboard_values")
    average_feedback_note = fields.Float(string="Moyenne des notes de feedback", compute="_compute_dashboard_values")

    @api.model
    def _compute_dashboard_values(self):
        # Calcul du nombre total de réclamations
        total = self.env['complaint.management'].sudo().search_count([])

        # Calcul du délai moyen de traitement
        total_days = 0
        total_resolved = 0
        for complaint in self.env['complaint.management'].sudo().search([]):
            if complaint.x_date_reception and complaint.x_date_resolution:
                total_days += (complaint.x_date_resolution - complaint.x_date_reception).days
                total_resolved += 1

        if total_resolved > 0:
            average_delay = total_days / total_resolved
        else:
            average_delay = 0

        # Calcul de la moyenne des notes de feedback
        total_feedback = 0
        total_feedback_count = 0
        for complaint in self.env['complaint.management'].sudo().search([]):
            if complaint.x_feedback_note:
                total_feedback += complaint.x_feedback_note
                total_feedback_count += 1

        if total_feedback_count > 0:
            average_feedback = total_feedback / total_feedback_count
        else:
            average_feedback = 0
    

        # Créer ou mettre à jour l'enregistrement unique du tableau de bord
        dashboard = self.search([], limit=1)
        if dashboard:
            dashboard.write({
                'total_complaints': total,
                'average_resolution_delay': average_delay,
                'average_feedback_note': average_feedback,
            })
        else:
            self.create({
                'total_complaints': total,
                'average_resolution_delay': average_delay,
                'average_feedback_note': average_feedback,
            })