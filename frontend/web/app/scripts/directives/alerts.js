(function () {
  angular
    .module('irma')
    .directive('alerts', Alerts);

  function Alerts(alerts) {
    return {
      restrict: 'E',
      template: '<div class="alerts"><ul class="list-unstyled">'
        + '<li class="alert-{{ alert.type }}" ng-repeat="alert in alerts" ng-click="dismiss(alert)" ng-bind-html="alert.message"></li>'
        + '</ul></div>',
      link(scope) {
        angular.extend(scope, {
          alerts: alerts.list(),
          dismiss: alert => alerts.remove(alert),
        });
      },
    };
  }
}());
