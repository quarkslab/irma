'use strict';

(function () {

  var dependencies = ['$timeout'];
  var Alerts = function ($timeout) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    // The array that stores the currently displayed alerts
    this.messages = [];

    this.map = {

      'uploadStart': {
        message: '<strong>Info: </strong> The upload has started',
        type: 'info',
        dismiss: 3000,
        status: 'debug'
      },
      'uploadCancel': {
        message: '<strong>Info: </strong> The upload was cancelled',
        type: 'info',
        dismiss: 3000,
        status: 'debug'
      },
      'uploadSuccess': {
        message: '<strong>Info: </strong> The upload was successful',
        type: 'info',
        dismiss: 3000,
        status: 'debug'
      },
      'uploadError': {
        message: '<strong>Info: </strong> The upload encountered errors. Please retry later.',
        type: 'danger',
        dismiss: false
      },
      'scanStart': {
        message: '<strong>Info: </strong> The scan has started',
        type: 'info',
        dismiss: 3000,
        status: 'debug'
      },
      'scanCancel': {
        message: '<strong>Info: </strong> The scan was cancelled',
        type: 'info',
        dismiss: 3000,
        status: 'debug'
      },
      'scanSuccess': {
        message: '<strong>Info: </strong> The scan was successful',
        type: 'info',
        dismiss: 3000,
        status: 'debug'
      },
      'apiError': {
        message: '<strong>Error:</strong> An error occured',
        type: 'danger',
        dismiss: false
      },
      'apiErrorWithMsg': {
        message: '<strong>Api Error:</strong> ',
        type: 'danger',
        dismiss: false
      }
    };

    this.autoDismiss = function(alert){

      if(alert.dismiss === undefined || alert.dismiss !== false){

        alert.dismiss = (alert.dismiss !== parseInt(alert.dismiss))? 4000: parseInt(alert.dismiss);

        $timeout(function(){
          this.remove(alert);
        }.bind(this), alert.dismiss);
      }
    };

    this.add = function(alert){
      // Tries to populate the alert with a standard one
      if(alert.standard && this.map[alert.standard]){
        alert = _.extend(alert, this.map[alert.standard]);
        if(alert.apiMsg){ alert.message += alert.apiMsg; }
      }

      if(alert.standard && !this.map[alert.standard]){
        alert = {
          message: '<strong>Missing alert:</strong> '+alert.standard,
          type: 'warning',
          dismiss: 5000
        };
      }

      // Adds a type if missing
      if(['info', 'warning', 'success', 'danger'].indexOf(alert.type) === -1){ alert.type = 'info';}

      if(alert.status !== 'debug'){
        this.messages.push(alert);
        this.autoDismiss(alert);
      }
    };

    this.remove = function(alert){
      var index = this.messages.indexOf(alert);
      if(index !== -1){
        this.messages.splice(index, 1);
      }
    };

    this.list = function(){
      return this.messages;
    };

  };

  Alerts.$inject = dependencies;
  angular.module('irma').service('alerts', Alerts);
}());
