'use strict';

(function () {

  var dependencies = ['$scope', 'state'];
  var Ctrl = function ($scope, state) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    if(!this.state.scan || this.state.status !== 'upload'){
      this.state.goTo('selection');
    }

    // Scope bindings
    this.$scope.cancel = this.cancel.bind(this);
  };

  Ctrl.prototype.cancel = function(){
    this.state.lastAction = 'cancelUpload';
    this.$scope.$emit('cancelUpload');
  };

  Ctrl.$inject = dependencies;
  angular.module('irma').controller('UploadCtrl', Ctrl);
}());