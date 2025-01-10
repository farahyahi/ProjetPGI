{
    "name": "Gestion des Réclamations",
    "version": "1.0",
    "category": "Services",
    "summary": "Module pour la gestion interne des réclamations",
    "author": "Farah Yahi",
    "depends": ["base", "mail" ,"website"],
    "data": [
        "security/security.xml",
        "views/complaint_views.xml",
        "views/technical_complaint_traitement_views.xml",
        "views/commercial_complaint_traitement_views.xml",
        "views/website_form.xml",
        "reports.xml",
    ],
    "installable": True,
    "application": True,
}
