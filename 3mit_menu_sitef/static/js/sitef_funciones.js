"use strict";

odoo.define("3mit_menu_sitef.admin", function (require) {
  var core = require("web.core");
  var _t = core._t;

  var FormController = require("web.FormController");
  var FormRenderer = require("web.FormRenderer");
  var FormView = require("web.FormView");
  var viewRegistry = require("web.view_registry");

  var Dialog = require("3mit.dialog");

  window.dlg = Dialog;

  const formController = FormController.extend({
    renderButtons: function () {
      this.$status = this.$(".status");

      const $footer = this.renderer.$("footer");
      $footer
        .children("button[name=click_me]")
        .on("click", this.doSitef.bind(this));

      // completa la construcción y reubicación de botones
      this._super.apply(this, arguments);
    },

    start: function () {
      var self = this;
      console.log("$el", this.$el);

      const data = this.model.get(this.handle).data;

      const restHost = data.sitef_restApi;

      $.ajax(restHost + "/sitef.js").then((rs) => {
        const sitef_script = rs + `; return getSitef("${restHost}",$);`;
        this.prepareSitef(sitef_script);
      });

      return this._super.apply(this, arguments).then(function () {});
    },

    prepareSitef(sitef_script) {
      this.sitef = Function(sitef_script)();
      window.sitef = this.sitef;
      if (!this.sitef) {
        this.displayNotification({
          type: "error",
          title: "Sitef",
          message: "Sin conección a 3MitSitef",
        });

        return;
      }
      //
      // captura eventos sitef
      this.sitef.on("statusMessage", (data) => {
        console.info("datos statusMessage:", data);
        this.setStatus(data);
      });
      this.sitef.on("transactionCompleted", (data) => {
        const self = this;
        const params = data.params;
        console.info("datos transactionCompleted:", data);
        //this.setStatus();
        const ret = data.responseValues["121"] || data.responseValues["122"];
        if (ret) {
          Dialog.alert(self, {
            title: _t("Sitef"),
            body: ret.replaceAll("\n", "<br>"),
            confirm_callback: function () {
              self.sitef.finalizarTransaccion({
                confirmationFlag: 1,
                saleInvoice: params.saleInvoice,
                invoiceDate: params.invoiceDate,
                invoiceTime: params.invoiceTime,
                value: params.value,
                operatorCode: params.operatorCode,
              });
              console.log(data);
            },
          });
        }
      });
      this.sitef.on("transactionError", (data) => {
        console.info("datos transactionError:", data);
      });
      this.sitef.on("transactionCanceled", (data) => {
        console.info("datos transactionCanceled:", data);
        this.setStatus(data);
      });
      this.sitef.on("confirm", (data, resolver) => {
        this.setStatus();

        Dialog.confirm(self, _t(data), {
          confirm_callback: function () {
            resolver("0");
          },
          cancel_callback: function () {
            resolver("1");
          },
          title: _t("Confirmation"),
        });
      });

      this.sitef.on("prompt", (data, resolver) => {
        this.setStatus();

        Dialog.prompt(self, {
          title: "Sitef",
          body: data.replaceAll("\n", "<br>"),
          confirm_callback: function (value) {
            resolver(value);
          },
        });
      });
      this.sitef.on("alert", (data, resolver) => {
        this.setStatus();

        Dialog.alert(self, {
          title: _t("Sitef"),
          body: data.replaceAll("\n", "<br>"),
          confirm_callback: function () {
            resolver(1);
          },
        });
      });

      this.sitef.on("select", (data, resolver) => {
        this.setStatus();

        const body = data.items.map((r) => {
          return `<div>${r.value} : ${r.text}</div>`;
        });
        Dialog.prompt(self, {
          title: data.title,
          body: body,
          confirm_callback: function (value) {
            resolver(value);
          },
        });
      });
    },
    doSitef() {
      const data = this.model.get(this.handle).data;

      switch (data.tipo_funcion) {
        case "anulacion":
          this.sitef
            .anularTransaccion({})
            .then((rs) => {
              console.log(">>>>", rs);
            })
            .catch((err) => {
              console.log("sitef Error", err);
            });
          break;
        case "cierre":
          this.sitef
            .cierreTerminal()
            .then(() => {
              console.log(">>>>", rs);
            })
            .catch((err) => {
              console.log("sitef Error", err);
            });
          break;
        case "admin":
          this.sitef
            .iniciarFuncion({ sitefFunction: 110 })
            .then(() => {
              console.log(">>>>", rs);
            })
            .catch((err) => {
              console.log("sitef Error", err);
            });
          break;
      }
    },
    setStatus(data) {
      let txt = data ? data : "";
      if (typeof data == "object") {
        txt = JSON.stringify(data);
      }
      this.$status.text(txt);
    },
    _onFieldChanged(ev) {
      this._super.apply(this, arguments);
      this.setStatus();
    },
  });

  const formView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
      Controller: formController,
    }),
  });

  viewRegistry.add("sitef_admin", formView);

  return formView;
});
