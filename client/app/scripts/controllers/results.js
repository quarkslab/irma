'use strict';

(function () {

  var dependencies = ['$scope', '$location', '$routeParams', 'alerts', 'state', 'config', 'ScanModel'];
  var Ctrl = function ($scope, $location, $routeParams, alerts, state, config, Scan) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    // Init controller
    if(!this.state.currentScan || !this.state.currentScan.id){
      // Came directly with the link, we build some things
      this.alerts.add({standard: 'loadingExistingResults'});
      this.state.currentScan = new Scan();
      this.state.currentScan.id = $routeParams.scan;
    }

    // Ask for the results
    this.state.currentScan.getResults().catch(function(){
      this.alerts.add({standard: 'noScanFound'});
      this.$location.path('/');
    }.bind(this));

    // Link the scan to the scope
    this.$scope.scan = this.state.currentScan;
    this.$scope.newScan = this.newScan.bind(this);
  };

  Ctrl.prototype.newScan = function(){
    this.state.trigger('newScan');
    this.$location.path('/');
  };


  Ctrl.$inject = dependencies;
  angular.module('irma').controller('ResultsCtrl', Ctrl);
}());