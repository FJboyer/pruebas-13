odoo.define('3mit_pos_delete_validation', function (require) {
    "use strict";
    var gui = require('point_of_sale.gui');
    var popups = require('point_of_sale.popups');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t  = require('web.core')._t;
    var chrome = require("point_of_sale.chrome");
    var screens = require('point_of_sale.screens');
    var rpc = require('web.rpc');

    var models= require('point_of_sale.models');
    var sucursal;
    models.load_models({
        model:  'res.company',
        fields: ['code_pos','delete_pass_dev', 'currency_id', 'email', 'website', 'company_registry', 'vat', 'name', 'phone', 'partner_id' , 'country_id', 'state_id', 'tax_calculation_rounding_method'],
        domain: [],
        loaded: function(self, companies){ 
            self.company = companies.find( company => company.id == self.company.id );
            sucursal = self.company;
        }
    });  

    chrome.OrderSelectorWidget.include({
        deleteorder_click_handler: function(event, $el) {
            var self  = this;
            var order = this.pos.get_order(); 
            if (!order) {
                return;
            } else if ( !order.is_empty() ){
                // SI LA SUCURSAL TIENE HABILITADO EL DESARROLLO
                if (sucursal.delete_pass_dev){
                    this.gui.show_popup('code-admin-popup',{
                    'title': 'Ingrese Clave de Administrador',
                    confirm: function(val){
                        if (sucursal.code_pos == val){
                            this.gui.show_popup('confirm',{
                                'title': _t('Destroy Current Order ?'),
                                'body': _t('You will lose any data associated with the current order'),
                                confirm: function(){
                                    self.pos.delete_current_order();
                                },
                            });
                        } else {
                            this.gui.show_popup('error', {
                                'title': 'Alerta: Clave Inválida',
                                'body': 'Disculpe, ingresó una clave nula o inválida',
                            })
                        }
                    },
                    });
                } else { // Revisar
                    this.gui.show_popup('confirm',{
                        'title': _t('Destroy Current Order ?'),
                        'body': _t('You will lose any data associated with the current order'),
                        confirm: function(){
                            self.pos.delete_current_order();
                        },
                    });
                }         
                //
            } else {
                this.pos.delete_current_order();
            }
        }
    })

    screens.NumpadWidget.include({
        start: function(){
            this._super();
        },
        clickDeleteLastChar: function() {
            var self = this
            if (sucursal.delete_pass_dev){ // Revisar
                this.gui.show_popup('code-admin-popup',{
                    'title': 'Ingrese Clave de Administrador',
                    confirm: function(val){
                        if (sucursal.code_pos == val){              
                            return self.state.deleteLastChar();
                        } else {
                            this.gui.show_popup('error', {
                                'title': 'Alerta: Clave Inválida',
                                'body': 'Disculpe, ingresó una clave nula o inválida',
                            })
                        }
                    },
                });
            } else {
                this._super();
            }
            
        },
        clickAppendNewChar: function(event) {
                var self = this
                if (sucursal.delete_pass_dev){ // Revisar
                    this.gui.show_popup('code-admin-popup',{
                        'title': 'Ingrese Clave de Administrador',
                        confirm: function(val){
                            if (sucursal.code_pos == val){
                                var newChar;
                                newChar = event.currentTarget.innerText || event.currentTarget.textContent;
                                return self.state.appendNewChar(newChar);
                                /* this._super(event) REVISAR*/
                            } else {
                                this.gui.show_popup('error', {
                                    'title': 'Alerta: Clave Inválida',
                                    'body': 'Disculpe, ingresó una clave nula o inválida',
                                })
                            }
                        },
                    });
                } else {
                    this._super(event)
                }                
        }
    })

    screens.ProductScreenWidget.include({
        _handleBufferedKeys: function () {
            var self = this
            var key_ev = this.buffered_key_events
            if(sucursal.delete_pass_dev) {
                if (this.buffered_key_events.length > 2) {
                    this.buffered_key_events = [];
                    return;
                }
                for (var i = 0; i < this.buffered_key_events.length; ++i) {
                    var ev = this.buffered_key_events[i];
                    if ((ev.key >= "0" && ev.key <= "9") || ev.key === ".") {     
                        if (sucursal.delete_pass_dev){ // Revisar
                            this.showAdminCodePopUp('num', ev.key, self)  
                        } else {
                            this.numpad.state.appendNewChar(ev.key);
                        }                           
                    }
                    else {
                        switch (ev.key){
                            case "Backspace":
                                if (sucursal.delete_pass_dev){ // Revisar
                                    this.showAdminCodePopUp('backspace', ev.key, self)
                                } else {
                                    this.numpad.state.deleteLastChar();
                                }                            
                                break;
                            case "Delete":
                                if (sucursal.delete_pass_dev){ // Revisar
                                    this.showAdminCodePopUp('delete', ev.key, self) 
                                } else {
                                    this.numpad.state.resetValue();
                                }                                                       
                                break;
                            case ",":
                                if (sucursal.delete_pass_dev){ // Revisar
                                    this.showAdminCodePopUp(',', ev.key, self)
                                } else {
                                    this.numpad.state.appendNewChar(".");
                                }                             
                                break;
                            case "+":
                                this.numpad.state.positiveSign();
                                break;
                            case "-":
                                this.numpad.state.negativeSign();
                                break;
                        }
                    }
                }
                this.buffered_key_events = [];
            } else {
                this._super();
            }         
        },
        showAdminCodePopUp: function (res, key, self){
            this.gui.show_popup('code-admin-popup',{
                'title': 'Ingrese Clave de Administrador',
                confirm: function(val){
                    if (sucursal.code_pos == val){ // Revisar
                        if(res == 'num'){
                           self.numpad.state.appendNewChar(key);    
                        } else if ( res == 'backspace'){
                            self.numpad.state.deleteLastChar();
                        } else if ( res == 'delete'){
                            self.numpad.state.resetValue();
                        } else if ( res == ','){
                            self.numpad.state.appendNewChar(".");
                        }                                                   
                    } else {
                        this.gui.show_popup('error', {
                            'title': 'Alerta: Clave Inválida',
                            'body': 'Disculpe, ingresó una clave nula o inválida',
                        })
                        return false;
                    }
                },
            }); 
        }
    })


    var CodeAdminPopup = popups.extend({
        template:'CodeAdminPopup',
        show: function(options){
            options = options || {};
            this._super(options);
    
            this.inputbuffer = '' + (options.value   || '');
            this.decimal_separator = _t.database.parameters.decimal_point;
            this.renderElement();
            this.firstinput = true;
        },
        click_numpad: function(event){
            var newbuf = this.gui.numpad_input(
                this.inputbuffer, 
                $(event.target).data('action'), 
                {'firstinput': this.firstinput}
                
                );
    
            this.firstinput = (newbuf.length === 0);
            
            if (newbuf !== this.inputbuffer) {
                this.inputbuffer = newbuf;
                //this.$('.value').text(this.inputbuffer);
                this.$('.value').text('*'.repeat(newbuf.length));
            }
        },
        click_confirm: function(){
            this.gui.close_popup();
            if( this.options.confirm ){
                this.options.confirm.call(this,this.inputbuffer);
            }
        },
    });
    gui.define_popup({name:'code-admin-popup', widget: CodeAdminPopup});
});