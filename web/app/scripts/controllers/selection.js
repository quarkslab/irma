'use strict';

(function () {

  var dependencies = ['$scope', 'alerts', 'state'];
  var Ctrl = function ($scope, alerts, state) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    this.state.newScan();

    // Bind things to scope
    this.$scope.start = this.start.bind(this);
    this.$scope.toggle = this.toggle.bind(this);
  };

  Ctrl.prototype.start = function(){
    if(this.state.noActiveProbes()){
      this.alerts.add({standard: 'noProbes'});
    } else {
      this.state.lastAction = 'startUpload';
      this.$scope.$emit('startUpload');
    }
  };

  Ctrl.prototype.toggle = function(probe){
    probe.active = !probe.active;
  };

  Ctrl.$inject = dependencies;
  angular.module('irma').controller('SelectionCtrl', Ctrl);
}());
