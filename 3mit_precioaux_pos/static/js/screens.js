odoo.define('custom_module_pos.widget_example', function (require) {
  'use strict';
  var screens = require('point_of_sale.screens');
  var field_utils = require('web.field_utils');
  var utils = require('web.utils');

  var tasa_dolar = 1;

  screens.OrderWidget.include({
    init: function (parent, options) {
      tasa_dolar = parent.pos.company_currency.rate;
      this._super(parent, options);
    },
    update_summary: function () {
      var self = this;
      let _order = this.pos.get_order();
      let _total = _order ? _order.get_total_with_tax() : 0;
      this._super();
      var monto = 0;
      if (tasa_dolar > 1) {
        monto = _total / tasa_dolar;
        monto = this.format_currency_no_symbol(monto, 2);
        _order.tasa_dolar = tasa_dolar;
      }
      if (self.el.querySelector('.summary .total .subdolar .value')) {
        self.el.querySelector('.summary .total .subdolar .value').textContent =
          monto;
      }
      _order.monto_total_dolar = monto;
    },
  });

  screens.PaymentScreenWidget.include({
    payment_input: function (input) {
      var paymentline = this.pos.get_order().selected_paymentline;
      if (
        this.payment_interface &&
        !['pending', 'retry'].includes(paymentline.get_payment_status())
      ) {
        return;
      }
      var newbuf = this.gui.numpad_input(this.inputbuffer, input, {
        firstinput: this.firstinput,
      });
      this.firstinput = newbuf.length === 0;
      if (this.gui.has_popup()) {
        return;
      }
      if (newbuf !== this.inputbuffer) {
        this.inputbuffer = newbuf;
        if (paymentline) {
          var amount = this.inputbuffer;
          if (this.inputbuffer !== '-') {
            amount = field_utils.parse.float(this.inputbuffer);
          }

          if (paymentline.payment_method.dolar_active) {
            var due_bs = this.pos.get_order().get_due(paymentline);
            var due_usd = utils.round_decimals(due_bs / tasa_dolar, 2);
            if (due_usd == amount) {
              paymentline.set_amount(due_bs);
            } else {
              paymentline.set_amount(amount * tasa_dolar);
            }
          } else {
            paymentline.set_amount(amount);
          }

          this.render_paymentlines();
          this.$('.paymentline.selected .edit').text(
            this.format_currency_no_symbol(amount)
          );
        }
      }
    },
    any_dolar: function (paymentlines) {
      return !!paymentlines.find((r) => r.payment_method.dolar_active);
    },

    reset_input: function () {
      var line = this.pos.get_order().selected_paymentline;
      this.firstinput = true;
      if (line) {
        if (line.payment_method.dolar_active) {
          this.inputbuffer = this.format_currency_no_symbol(
            line.get_amount() / tasa_dolar
          );
        } else {
          this.inputbuffer = this.format_currency_no_symbol(line.get_amount());
        }
      } else {
        this.inputbuffer = '';
      }
    },
  });
});
