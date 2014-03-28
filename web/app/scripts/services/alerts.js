'use strict';

angular.module('irma')
.factory('alerts', ['$timeout', function($timeout){
  var messages = [], alerts, autoDismiss;

  autoDismiss = function(alert){
    
    if(alert.dismiss === undefined || alert.dismiss !== false){

      alert.dismiss = (alert.dismiss != parseInt(alert.dismiss))? 4000: parseInt(alert.dismiss);
      $timeout(function(){
        var index = messages.indexOf(alert);
        if(index !== -1){
          messages.splice(index, 1);
        }
      },alert.dismiss);
    }
  };

  alerts = {
    add: function(alert){
      if(['info', 'warning', 'success', 'danger'].indexOf(alert.type) == -1)
        alert.type = 'info';

      if(alert.status !== 'debug'){
        messages.push(alert);
        autoDismiss(alert);
      }
    },
    list: function(){
      return messages;
    }
  }

  return alerts;
}]);