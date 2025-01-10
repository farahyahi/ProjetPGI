from odoo import models, fields, api # type: ignore warning

class Complaint(models.Model):
    _name = 'complaint.management'
    _description = 'Gestion interne des réclamations'

    x_agence_id = fields.Many2one(
        "res.company",
        string="Agence",
         # non required to test
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

    # Historique des actions
    action_history = fields.One2many('complaint.action', 'complaint_id', string='Historique des actions')

    # Historique des appels
    call_history = fields.One2many('complaint.call', 'x_complaint_id', string='Historique des appels')    
    
    x_feedback_note = fields.Integer(string="Note de satisfaction (/5)")
    x_feedback_description = fields.Text(string="Commentaires")
    
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