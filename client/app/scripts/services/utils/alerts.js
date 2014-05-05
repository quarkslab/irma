'use strict';

(function () {

  var dependencies = ['$timeout'];
  var Alerts = function ($timeout) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    // The array that stores the currently displayed alerts
    this.messages = [];

    this.map = {
      'apiError': {
        message: '<strong>Error:</strong> Unable to get response from API',
        type: 'danger',
        dismiss: false
      },
      'noFilesToUpload': {
        message: '<strong>Warning:</strong> There are no files queued for upload',
        type: 'warning',
        dismiss: 5000
      },
      'scanIdRetrievalError': {
        message: '<strong>Error:</strong> An error occured while requesting a new scan id',
        type: 'danger',
        dismiss: false
      },
      'probesListError': {
        message: '<strong>Error:</strong> Unable to load probes list',
        type: 'danger',
        dismiss: false
      },
      'uploadStarted': {
        message: '<strong>Info:</strong> Upload has started...',
        type: 'info',
        dismiss: 2000
      },
      'uploadCanceled': {
        message: '<strong>Warning:</strong> Upload was canceled',
        type: 'warning',
        dismiss: 5000
      },
      'errorInUpload': {
        message: '<strong>Error:</strong> An error occured during upload',
        type: 'danger',
        dismiss: false
      },
      'uploadComplete': {
        message: '<strong>Info:</strong> The upload was successfull',
        type: 'info',
        dismiss: 2000
      },
      'scanStarted': {
        message: '<strong>Info:</strong> Scan has started...',
        type: 'info',
        dismiss: 2000
      },
      'scanCanceled': {
        message: '<strong>Warning:</strong> Scan was canceled',
        type: 'warning',
        dismiss: 5000
      },
      'scanComplete': {
        message: '<strong>Info:</strong> The scan was successfull',
        type: 'info',
        dismiss: 2000
      },
      'loadingExistingResults': {
        message: '<strong>Info:</strong> Loading an existing scan',
        type: 'info',
        dismiss: 2000
      },
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
      if(alert.standard && this.map[alert.standard]){ alert = _.extend(alert, this.map[alert.standard]);}

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