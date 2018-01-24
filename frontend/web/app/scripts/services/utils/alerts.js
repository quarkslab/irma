(function () {
  'use strict';

  angular
    .module('irma')
    .factory('alerts', Alerts);

  Alerts.$inject = ['$timeout'];

  // With the Hug migration, some of the `map` message aren't not use anymore.
  // There is a need to take a deep look at this factory to check if it is
  // necessary to keep the complexity of different messages, or just on
  // (apiErrorWithMsg) to display error messages from the API.
  // See IRMA-656
  function Alerts($timeout) {
    // The array that stores the currently displayed alerts
    var messages = [];
    var map = {
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
      'ftpError': {
        message: '<strong>Error:</strong> An FTP error occured',
        type: 'danger',
        dismiss: false
      },
      'apiErrorWithMsg': {
        message: '<strong>Api Error:</strong> ',
        type: 'danger',
        dismiss: false
      }
    };

    var service = {
      add: add,
      autoDismiss: autoDismiss,
      list: list,
      remove: remove,
      removeAll: removeAll
    };

    return service;

    function autoDismiss(alert) {
      if (alert.dismiss === undefined || alert.dismiss !== false) {
        alert.dismiss = (alert.dismiss !== parseInt(alert.dismiss)) ? 4000 : parseInt(alert.dismiss);

        $timeout(function(){
          remove(alert);
        }, alert.dismiss);
      }
    }

    function add(alert) {
      // Tries to populate the alert with a standard one
      if (alert.standard && map[alert.standard]) {
        alert = _.extend(alert, map[alert.standard]);

        if (alert.apiMsg) {
          // The API should not return multiple errors, but in case there can
          // be multiple, this function display all API Errors separate with a
          // comma.
          alert.message += _.map(alert.apiMsg, function(message) {
            return message;
          }).join(", ");
        }
      }

      if (alert.standard && !map[alert.standard]) {
        alert = {
          message: '<strong>Missing alert:</strong> '+ alert.standard,
          type: 'warning',
          dismiss: 5000
        };
      }

      // Adds a type if missing
      if (['info', 'warning', 'success', 'danger'].indexOf(alert.type) === -1) { alert.type = 'info'; }

      if (alert.status !== 'debug') {
        messages.push(alert);
        autoDismiss(alert);
      }
    }

    function remove(alert) {
      var index = messages.indexOf(alert);
      if(index !== -1){
        messages.splice(index, 1);
      }
    }

    function removeAll() {
      _(messages).map(function (item) { remove(item); });
    }

    function list() {
      return messages;
    }
  }
}) ();
