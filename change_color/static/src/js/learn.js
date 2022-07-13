odoo.define('learn_js.odoo_tutorial', function (require) {
    'use strict';
    console.log('JS loaded');
    var FormController = require('web.FormController');
     var ExtendFormController = FormController.include({
        saveRecord: function () {
        var res = this._super.apply(this, arguments);
            console.log(res);
            if (this.modelName == 'purchase.order'){
               this.do_notify('Success', 'Record Saved');
               self = this
               self._rpc({
               model: 'purchase.order',
               method: 'search_read',
               fields: ['name'],
               context: self.context,
               }).then(function(result){
               console.log(result)
               })
            }
        return res
        }
     });
});