'use strict';

(function () {

  var dependencies = ['$scope', 'state'];
  var Ctrl = function ($scope, state) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    if(!this.state.scan ||  this.state.status !== 'scan'){
      this.state.goTo('selection');
    }
    
    // Scope bindings
    this.$scope.cancel = this.cancel.bind(this);
  };

  Ctrl.prototype.cancel = function(){
    this.state.lastAction = 'cancelScan';
    this.$scope.$emit('cancelScan');
  };

  Ctrl.$inject = dependencies;
  angular.module('irma').controller('ScanCtrl', Ctrl);
}());