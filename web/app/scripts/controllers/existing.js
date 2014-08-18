'use strict';

(function () {

  var dependencies = ['$scope', 'state'];
  var Ctrl = function ($scope, state) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    this.$scope.goToScan = this.goToScan.bind(this);
  };

  Ctrl.prototype.goToScan = function(id){
    this.state.goTo('results', id);
  };

  Ctrl.$inject = dependencies;
  angular.module('irma').controller('ExistingCtrl', Ctrl);
}());