odoo.define('complaintManagement.complaint_form', function (require) {
    "use strict";

    const publicWidget = require('web.public.widget');

    publicWidget.registry.ComplaintForm = publicWidget.Widget.extend({
        selector: 'form[action="/create/webcomplaint"]',
        events: {
            'change #complaint_origine': '_onOrigineChange',
        },

        /**
         * Handle the change event for the origine field.
         * Show/hide the "raison sociale" field based on the selected value.
         */
        _onOrigineChange: function (ev) {
            const origine = ev.target.value;
            const raisonSocialeField = document.getElementById('raison_sociale_field');
            const raisonSocialeInput = document.getElementById('complaint_raison_sociale');

            if (origine === 'Entreprise') {
                raisonSocialeField.classList.remove('d-none');
                raisonSocialeInput.setAttribute('required', 'required');
            } else {
                raisonSocialeField.classList.add('d-none');
                raisonSocialeInput.removeAttribute('required');
            }
        },
    });
});
