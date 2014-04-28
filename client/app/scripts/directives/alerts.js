'use strict';

(function () {

  var dependencies = ['alerts'];
  var Alerts = function (alerts) {

    return {
      restrict: 'E',
      template: '<div class="alerts"><ul class="list-unstyled">'+
        '<li class="alert-{{alert.type}}" ng-repeat="alert in alerts" ng-click="dismiss(alert)" ng-bind-html="alert.message"></li>'+
        '</ul></div>',
      link: function(scope, element, attr) {
        scope.alerts = alerts.list();

        scope.dismiss = function(alert){ alerts.remove(alert);};
      }
    };

  };

  Alerts.$inject = dependencies;
  angular.module('irma').directive('alerts', Alerts);
}());
