odoo.define('point_of_sale.validacion_cliente', function(require) {
"use strict";
var screens = require('point_of_sale.screens');
var gui = require('point_of_sale.gui');
var core = require('web.core');
var rpc = require('web.rpc');
var QWeb = core.qweb;
var _t = core._t;
screens.ClientListScreenWidget.include({
    save_client_details: function(partner) {
        var self = this;
        var fields = {};
        this.$('.client-details-contents .detail').each(function(idx,el){
            if (self.integer_client_details.includes(el.name)){
                var parsed_value = parseInt(el.value, 10);
                if (isNaN(parsed_value)){
                    fields[el.name] = false;
                }
                else{
                    fields[el.name] = parsed_value
                }
            }
            else{
                fields[el.name] = el.value || false;
            }
        });

        if (!fields.name) {
            this.gui.show_popup('error',{
                'title': _t("Verificar"),
                'body':  _t("El nombre del cliente es requerido."),
            });
            return;
        }

        if (fields.company_type === 'company'){
            if (!fields.vat){
            this.gui.show_popup('error',{
                'title': _t("Verificar"),
                'body':  _t("El RIF de la Compañia es requerido."),
            });
            return;
            }
            if (!fields.street){
            this.gui.show_popup('error',{
                'title': _t("Verificar"),
                'body':  _t("Debe llenar la dirección (Calle)."),
            });
            return;
            }
            if (!fields.city){
            this.gui.show_popup('error',{
                'title': _t("Verificar"),
                'body':  _t("Debe llenar la dirección (Ciudad)."),
            });
            return;
            }
            if (!fields.country_id){
            this.gui.show_popup('error',{
                'title': _t("Verificar"),
                'body':  _t("Debe llenar la dirección (País)."),
            });
            return;
            }
            if (!fields.state_id){
            this.gui.show_popup('error',{
                'title': _t("Verificar"),
                'body':  _t("Debe llenar la dirección (Estado)."),
            });
            return;
            }
            if (!fields.zip){
            this.gui.show_popup('error',{
                'title': _t("Verificar"),
                'body':  _t("Debe llenar la dirección (Código Postal)."),
            });
            return;
            }


        }
        if(fields.vat){
            var RegExPattern = /^(V|E|J|P|G){1}(-){1}([0-9]){9}$/;
            if (fields.vat.match(RegExPattern)) {
              var errorMessage = '';
            } else {
                 this.gui.show_popup('error',{
                'title': _t("Verificar"),
                'body':  _t("El RIF del cliente es Invalido. Debe tener el formato V-000000005 con un tamaño de 9 caracteres numericos, de poseer menos, rellenar con ceros luego del '-'."),
                });
                return;
            }

        }

        if (fields.company_type === 'person'){
            if (!fields.identification_id){
            this.gui.show_popup('error',{
                'title': _t("Verificar"),
                'body':  _t("El Documento de Identidad del cliente es requerido."),
            });
            return;
            }
            if (!fields.street){
            this.gui.show_popup('error',{
                'title': _t("Verificar"),
                'body':  _t("Debe llenar la dirección (Calle)."),
            });
            return;
            }
        }
        if (fields.identification_id){
            var RegExPattern = /^([0-9]){6,8}$/;
            if (fields.identification_id.match(RegExPattern)) {
              var errorMessage = '';
            } else {
                 this.gui.show_popup('error',{
                'title': _t("Verificar"),
                'body':  _t("El Documento de Identidad del cliente es Invalido. Debe tener el formato 00000000 sin puntos."),
                });
                return;
            }
        }

        if (fields.email){
            var RegExPattern = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,4})+$/;
            if (fields.email.match(RegExPattern)) {
              var errorMessage = '';
            } else {
                 this.gui.show_popup('error',{
                'title': _t("Verificar"),
                'body':  _t("El correo es invalido, por favor ingrese un correo valido."),
                });
                return;
            }

        }

        if (this.uploaded_picture) {
            fields.image_1920 = this.uploaded_picture;
        }

        fields.id = partner.id || false;

        var contents = this.$(".client-details-contents");
        contents.off("click", ".button.save");

        rpc.query({
                model: 'res.partner',
                method: 'create_from_ui',
                args: [fields],
            })
            .then(function(partner_id){
                if (partner_id === 'Ya existe'){
                    self.gui.show_popup('error',{
                    'title': _t("Verificar"),
                    'body':  _t("Ya existe un registro de CI o RIF asignado a otro cliente."),
                    });
                    return;
                }
                self.saved_client_details(partner_id);
            }).catch(function(error){
                error.event.preventDefault();
                var error_body = _t('Your Internet connection is probably down.');
                if (error.message.data) {
                    var except = error.message.data;
                    error_body = except.arguments && except.arguments[0] || except.message || error_body;
                }
                self.gui.show_popup('error',{
                    'title': _t('Error: Could not Save Changes'),
                    'body': error_body,
                });
                contents.on('click','.button.save',function(){ self.save_client_details(partner); });
            });
    },

});

return screens;

});
