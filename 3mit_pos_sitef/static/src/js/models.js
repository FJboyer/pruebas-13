odoo.define("pos_sitef.models", function (require) {
  var models = require("point_of_sale.models");
  var PaymentSitef = require("pos_sitef.payment");

  models.register_payment_method("sitef", PaymentSitef);
  models.load_fields("pos.payment.method", [
    "sitef_restApi",
    "sitef_methodType",
    //"sitef_script",
  ]);

  var _super_paymentline = models.Paymentline.prototype;
  models.Paymentline = models.Paymentline.extend({
    initialize: function (attributes, options) {
      this.payment_statusInfo = null;
      _super_paymentline.initialize.call(this, attributes, options);
    },
    set_payment_statusInfo: function (value) {
      this.payment_statusInfo = value;
      this.pos.trigger("change:payment_statusInfo", value);
    },
    /* set_payment_status: function (value) {
      _super_paymentline.set_payment_status.call(this, value);
      this.pos.trigger("change:payment_status", value);
    }, */
  });
});
