odoo.define("pos_sitef.payment", function (require) {
  ("use strict");

  var core = require("web.core");
  var chrome = require("point_of_sale.chrome");
  var PaymentInterface = require("point_of_sale.PaymentInterface");

  var _t = core._t;
  //
  require("3mit_pos_sitef.popups");

  var screens = require("point_of_sale.screens");
  screens.PaymentScreenWidget.include({
    init: function (parent, options) {
      this._super(parent, options);
      var self = this;
      window.psw = this;
      this.pos.bind("change:payment_statusInfo", function (data) {
        //self.$("#sitef_payment_statusInfo").text(data.toString());
        const current_screen = self.chrome.gui.current_screen;
        current_screen.render_paymentlines();
      });

      this.pos.bind("change:payment_status", function (data) {
        const current_screen = self.chrome.gui.current_screen;
        if (current_screen) {
          // current_screen.render_paymentlines();
        }
      });
    },
    //willStart:
    Xclick_delete_paymentline: async function (cid) {
      var lines = this.pos.get_order().get_paymentlines();
      for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        if (line.cid === cid) {
          // If a paymentline with a payment terminal linked to
          // it is removed, the terminal should get a cancel
          // request.
          if (
            ["waiting", "waitingCard", "timeout"].includes(
              lines[i].get_payment_status()
            )
          ) {
            var bCancel =
              await line.payment_method.payment_terminal.send_payment_cancel(
                this.pos.get_order(),
                cid
              );
            if (!bCancel) {
              return;
            }
          }

          this.pos.get_order().remove_paymentline(line);
          this.reset_input();
          this.render_paymentlines();
          return;
        }
      }
    },
  });
  //
  var PaymentSitef = PaymentInterface.extend({
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------
    /**
     * @override
     */
    init: function () {
      this._super.apply(this, arguments);

      const restHost = this.payment_method.sitef_restApi;

      $.ajax(restHost + "/sitef.js").then((rs) => {
        this.payment_method.sitef_script =
          rs + `; return getSitef("${restHost}",$);`;
        this.initSitef();
      });
    },
    initSitef: function () {
      const self = this;
      this.transaction = null;

      //this.enable_reversals();

      if (!this.payment_method.sitef_script) {
        return;
      }

      this.sitef = Function(this.payment_method.sitef_script)();
      //
      //this.sitef = window.sitef.getSitef("http://localhost:5000", $);
      //
      this.sitef.on("statusMessage", this._onStatusMessage.bind(this));

      this.payment_method.sitef = this.sitef;
      if (this.payment_method.id == 6) {
        window.ps = this;
        window.sitef = this.sitef;
      }

      console.log("**** paymentMethod", this.payment_method);

      this.sitef.on("confirm", (data, resolver) => {
        if (data.indexOf("DEBE COLECTAR MONTO") > -1) {
          return resolver("1");
        }

        this.pos.gui.show_popup("confirm", {
          title: "Popup Title",
          body: data,
          confirm: function () {
            return resolver("0");
          },
          cancel: function () {
            return resolver("1");
          },
        });
      });
      this.sitef.on("prompt", (data, resolver) => {
        /*const client = self.get_order().getClient();
        const ci = client.vat || client.identification_id || "";
        */
        //this.pos.gui.current_screen.hide();
        this.enableKeyHandlers(false);
        this.pos.gui.show_popup("textinput", {
          title: data,
          confirm: function (value) {
            this.pos.gui.current_screen.show();
            resolver(value);
          },
          cancel: function () {
            //this.pos.gui.current_screen.show();
            this.enableKeyHandlers(true);
            self.sitef.cancelarTransaccion().then(() => {
              resolver(null);
            });
          },
        });
      });
      this.sitef.on("alert", (data, resolver) => {
        //window.alert(data);
        resolver();
      });
      this.sitef.on("select", ({ title, items }, resolver) => {
        if (title == "SELECCIONE LA FORMA DE PAGO") {
          resolver("1");
          return;
        }
        this.pos.gui.show_popup("selection", {
          title: title,
          list: items.map((r) => {
            return { label: r.text, item: r.value };
          }),
          confirm: function (item) {
            resolver(item);
          },
          cancel: function () {
            self.sitef.cancelarTransaccion().then(() => {
              resolver(null);
            });
          },
        });
      });

      this.sitef.on("transactionCompleted", (sitef_data) => {
        const self = this;
        const params = sitef_data.params;
        //
        const body = sitef_data.responseValues[121].replace("\n", "<br>");
        this.pos.gui.show_popup("sitef-voucher", {
          title: "Voucher Sitef",
          body: body,
          confirm: function () {
            self.sitef.finalizarTransaccion({
              confirmationFlag: 1,
              saleInvoice: params.saleInvoice,
              invoiceDate: params.invoiceDate,
              invoiceTime: params.invoiceTime,
              value: params.value,
              operatorCode: params.operatorCode,
            });
          },
          cancel: function () {
            return;
          },
        });
      });

      this.sitef.on("transactionCanceled", () => {
        const order = this.pos.get_order();
        const paymentline = order.selected_paymentline;

        //paymentline.set_payment_statusInfo(null);
      });
    },

    enableKeyHandlers(bEnable) {
      if (!bEnable) {
        $("body").off("keypress", this.keyboard_handler);
        $("body").off("keydown", this.keyboard_keydown_handler);
      } else {
        // that one comes from BarcodeEvents
        $("body").keypress(this.keyboard_handler);
        // that one comes from the pos, but we prefer to cover all the basis
        $("body").keydown(this.keyboard_keydown_handler);
      }
    },
    /**
     * @override
     */
    send_payment_request: function (cid) {
      const order = this.pos.get_order();
      const paymentline = order.selected_paymentline;

      paymentline.set_payment_statusInfo(null);

      if (!this.sitef) {
        this.pos.gui.show_popup("error", {
          title: _t("Terminal Error"),
          body: _t("Sin conexión a 3mitSitef server"),
        });

        return Promise.resolve(false);
      }

      //TODO: Revisar necesidad de redondeo ??
      var amount = Number(paymentline.amount.toFixed(2));
      //
      var transaction;
      if (this.payment_method.sitef_methodType == 3) {
        transaction = this.sitef.pagoTarjetaCredito({
          //transaction = this.sitef.iniciarPago({
          saleInvoice: order.uid,
          value: amount,
          operator: this.pos.pos_session.user_id[1],
        });
      }
      if (this.payment_method.sitef_methodType == 2) {
        transaction = this.sitef.pagoTarjetaDebito({
          saleInvoice: order.uid,
          value: amount,
          operator: this.pos.pos_session.user_id[1],
        });
      }
      paymentline.set_payment_status("waitingCard");

      //resuelta la transacción devuelve true/false
      return transaction.then((rs) => {
        if (rs.ret == 0) {
          return true;
        } else {
          if (rs.ret < 0) {
            paymentline.set_payment_statusInfo(
              "CANCELADO CON CODIGO " + rs.ret
            );
          }
          return false;
        }
      });
    },
    send_payment_cancel: function (order, cid) {
      const paymentline = order.selected_paymentline;

      return this.sitef.cancelarTransaccion().then((rs) => {
        return true;

        //hay que esperar a que finalice la transaccion
        return new Promise((resolve) => {
          var id = setInterval(() => {
            // si hay respuesta de la transacción, permite continuar con cancelar
            var status = paymentline.get_payment_status();
            console.log("status", status);
            if (
              ["done", "retry", "canceled", "waitingCancel"].includes(status)
            ) {
              clearInterval(id);
              if (status == "waitingCancel") {
                //paymentline.status = "retry";
              }
              return resolve(status == "canceled");
            }
          }, 100);
        });
      });
    },

    /**
     * @override
     */
    send_payment_reversal: function () {
      this._super.apply(this, arguments);
      alert("not implemented");

      /*
      this.pos.get_order().selected_paymentline.set_payment_status("reversing");
      return this._sendTransaction(timapi.constants.TransactionType.reversal);
      */
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    _onStatusMessage: function (data) {
      var paymentline = this.pos.get_order().selected_paymentline;
      if (!paymentline) {
        return;
      }
      var s = typeof data === "object" ? data.status : data;
      paymentline.set_payment_statusInfo(s);
    },

    _onTransactionComplete: function (event, data) {
      alert("not implemented yet");
      return transactionResolve();
      // imprimir, confirmar, guardar datos?
      this.sitef.finalizarTransaccion({ confirmationFlag: 1 });

      timapi.DefaultTerminalListener.prototype.transactionCompleted(
        event,
        data
      );

      if (event.exception) {
        var line = this.pos.get_order().selected_paymentline;
        if (line && line.get_payment_status() !== "retry") {
          this.pos.gui.show_popup("error", {
            title: _t("Terminal Error"),
            body: _t("Transaction was not processed correctly"),
          });
        }

        this.transactionResolve();
      } else {
        if (data.printData) {
          this._printReceipts(data.printData.receipts);
        }

        // Store Transaction Data
        var transactionData = new timapi.TransactionData();
        transactionData.transSeq = data.transactionInformation.transSeq;
        this.terminal.transactionData = transactionData;

        this.transactionResolve(true);
      }
    },

    _printReceipts: function (receipts) {
      _.forEach(receipts, (receipt) => {
        var value = receipt.value.replace(/\n/g, "<br />");
        if (
          receipt.recipient === timapi.constants.Recipient.merchant &&
          this.pos.proxy.printer
        ) {
          this.pos.proxy.printer.print_receipt(
            "<div class='pos-receipt'><div class='pos-payment-terminal-receipt'>" +
              value +
              "</div></div>"
          );
        } else if (
          receipt.recipient === timapi.constants.Recipient.cardholder
        ) {
          this.pos.get_order().selected_paymentline.set_receipt_info(value);
        }
      });
    },
  });

  return PaymentSitef;
  return {
    models: server_data.models,
    PaymentSitef,
  };
});
