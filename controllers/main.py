# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import base64
from werkzeug.datastructures import FileStorage


class Complaint(http.Controller):

    @http.route('/complaint_webform', type='http', auth='public', website=True)
    def complaint_webform(self, **kw):
        return request.render('complaintManagement.create_complaint', {})

    @http.route('/create/webcomplaint', type='http', auth='public', website=True, csrf=False)
    def create_webcomplaint(self, **kw):
        
        nom = kw.get('complaint_nom')
        adresse = kw.get('complaint_adresse')
        commune = kw.get('complaint_commune')
        telephone = kw.get('complaint_telephone')
        email = kw.get('complaint_email')
        raison_sociale = kw.get('complaint_raison_sociale')
        type_contact = kw.get('complaint_origine')

        # Créer un nouveau partenaire dans res.partner
        partner_data = {
            'name': nom,
            'street': adresse,
            'city': commune,
            'phone': telephone,
            'email': email,
            'x_raison_sociale' : raison_sociale,
            'x_type_contact' : type_contact
        }


        partner = request.env['res.partner'].sudo().create(partner_data)         
        
        uploaded_files = request.httprequest.files.getlist('complaint_attachements')

        attachment_ids = []
        if uploaded_files:
          for uploaded_file in uploaded_files:
            file_data = base64.b64encode(uploaded_file.read())
            attachment = request.env['ir.attachment'].sudo().create({
                'name': uploaded_file.filename,
                'datas': file_data,
                'type': 'binary',
                'res_model': 'complaintManagement.complaint.management',  # Replace with the appropriate model
                'res_id': 0,  # ID of the related complaint record
            })
            attachment_ids.append(attachment.id)
         
         

        request.env['complaint.management'].sudo().create({  
            'x_reclamant': partner.id,
            'x_objet': kw.get('complaint_objet'),
            'x_description': kw.get('complaint_description'),
            'x_origine': kw.get('complaint_origine'),
            'x_attachements': [(4, attachment_id) for attachment_id in attachment_ids] if attachment_ids else [],
        })        


        return request.render("complaintManagement.complaint_thanks", {})
