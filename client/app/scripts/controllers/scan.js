'use strict';

(function () {

  var dependencies = ['$scope', '$location', '$timeout', 'constants', 'alerts', 'state', 'config', 'ScanModel'];
  var Ctrl = function ($scope, $location, $timeout, constants, alerts, state, config, Scan) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    // If no current scan is set, we reset the route to the selection
    if(!this.state.currentScan){ return this.$location.path('/');}

    // Scope bindings
    $scope.scan = this.state.currentScan;
    $scope.cancel = this.cancelScan.bind(this);

    // Launch scan
    $timeout(function(){
      this.state.currentScan.launchScan().then(function(){
        this.alerts.add({standard: 'scanStarted'});
      }.bind(this));
    }.bind(this), constants.speed);
  };

  Ctrl.prototype.cancelScan = function(){
    this.state.currentScan.cancelScan().then(function(){
      this.alerts.add({standard: 'scanCanceled'});
      this.$location.path('/');
    }.bind(this));
  };

  Ctrl.$inject = dependencies;
  angular.module('irma').controller('ScanCtrl', Ctrl);
}());