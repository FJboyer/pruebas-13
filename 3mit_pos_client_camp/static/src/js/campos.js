odoo.define('point_of_sale.pos_campos', function(require) {
"use strict";
var screens = require('point_of_sale.screens');
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;
var models = require('point_of_sale.models');
var PosModelSuper = models.PosModel;


models.load_fields("res.partner",['people_type_individual','nationality','identification_id','company_type']);

screens.PaymentScreenWidget.include({
     validate_order: function(force_validation) {
        if (this.order_is_valid(force_validation)) {
            if ( !this.pos.get_order().attributes.client ){
                this.gui.show_popup('error',{
                    'title': _t("Verificar"),
                    'body':  _t("El Cliente debe estar Seleccionado."),
                });
                return;
            }
            this.finalize_validation();
        }
    },

});


});

