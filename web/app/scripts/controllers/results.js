'use strict';

(function () {

  var dependencies = ['$scope', '$routeParams', 'state'];
  var Ctrl = function ($scope, $routeParams, state) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    // Init controller
    if(this.state.status !== 'results'){
      this.state.newScan($routeParams.scan);
      this.state.scan.getResults();
    }

    // Link the scan to the scope
    this.$scope.newScan = this.newScan.bind(this);
  };

  Ctrl.prototype.newScan = function(){
    this.state.newScan();
    this.state.goTo('selection');
  };


  Ctrl.$inject = dependencies;
  angular.module('irma').controller('ResultsCtrl', Ctrl);
}());