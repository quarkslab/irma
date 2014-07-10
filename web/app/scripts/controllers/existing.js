'use strict';

(function () {

  var dependencies = ['$scope', '$location', 'alerts', 'state', 'config', 'ScanModel'];
  var Ctrl = function ($scope, $location, alerts, state, config, Scan) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    this.state.currentScan = new Scan();
    $scope.goToScan = this.goToScan.bind(this);
    $scope.newScan = this.newScan.bind(this);
  };

  Ctrl.prototype.goToScan = function(id){
    this.state.trigger('goToResults');
    this.$location.path('/results/'+id);
  };

  Ctrl.prototype.newScan = function(){
    this.state.trigger('newScan');
    this.$location.path('/');
  };

  Ctrl.$inject = dependencies;
  angular.module('irma').controller('ExistingCtrl', Ctrl);
}());