odoo.define('pos_product_list.models', function (require) {
  'use strict';

  var pos_model = require('point_of_sale.models');

  pos_model.load_fields('product.product', [
    'qty_available',
    'default_code',
    'list_price',
    'aux_price',
  ]);
  pos_model.load_fields('pos.payment.method', ['dolar_active']);

  var models = require('point_of_sale.models');
  var _super_order = models.Order.prototype;
  var _super_orderline = models.Orderline.prototype;
  var rpc = require('web.rpc');
  var utils = require('web.utils');
  var round_pr = utils.round_precision;
  var exports = { Paymentline: models.Paymentline };

  models.Order = models.Order.extend({
    initialize: function (attributes, options) {
      _super_order.initialize.call(this, attributes, options);
      this.printNumber = 0;
      this.discount_total = 0;
      this.monto_total_dolar = 0;
      this.tasa_dolar = 1;
      this.multi = 1;
    },

    obtener_subtotal: function () {
      return this.get_total_without_tax();
    },

    //   MODIFICACIONES PARA GESTIONAR PAGOS EN $

    add_paymentline: function (payment_method) {
      _super_order.add_paymentline.call(this, payment_method);
      if (payment_method.dolar_active) {
        this.selected_paymentline.set_amount(0);
      }
    },
  });

  //exports.Paymentline = Backbone.Model.include({
  //    initialize: function(attributes, options) {
  //        this.pos = options.pos;
  //        this.order = options.order;
  //        this.amount = 0;
  //        this.selected = false;
  //        this.ticket = '';
  //        this.payment_status = '';
  //        this.card_type = '';
  //        this.transaction_id = '';
  //
  //        if (options.json) {
  //            this.init_from_JSON(options.json);
  //            return;
  //        }
  //        this.payment_method = options.payment_method;
  //        if (this.payment_method === undefined) {
  //            throw new Error(_t('Please configure a payment method in your POS.'));
  //        }
  //        this.name = this.payment_method.name;
  //    },
  //
  //    export_as_JSON: function(){
  //        return {
  //            name: time.datetime_to_str(new Date()),
  //            payment_method_id: this.payment_method.id,
  //            amount: this.get_amount()/this.tasa_dolar,
  //            payment_status: this.payment_status,
  //            ticket: this.ticket,
  //            card_type: this.card_type,
  //            transaction_id: this.transaction_id,
  //        };
  //    },
  //});
});
