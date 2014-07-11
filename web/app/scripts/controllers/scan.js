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

    $scope.$on('scanComplete', function(event){
      this.$location.path('/results/'+this.state.currentScan.id);
      this.alerts.add({standard: 'scanComplete'});
    }.bind(this));
  };

  Ctrl.prototype.cancelScan = function(){
    this.state.trigger('cancelScan');
    this.state.currentScan.cancelScan().finally(function(){
      this.alerts.add({standard: 'scanCanceled'});
      this.$location.path('/');
    }.bind(this));
  };

  Ctrl.$inject = dependencies;
  angular.module('irma').controller('ScanCtrl', Ctrl);
}());