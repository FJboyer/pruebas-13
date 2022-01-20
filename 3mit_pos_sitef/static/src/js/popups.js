odoo.define("3mit_pos_sitef.popups", function (require) {
  "use strict";

  var gui = require("point_of_sale.gui");
  var PopupWidget = require("point_of_sale.popups");

  var SitefVoucher = PopupWidget.extend({
    template: "3mit_pos_sitef.voucher",
  });

  gui.define_popup({
    name: "sitef-voucher",
    widget: SitefVoucher,
  });
});
