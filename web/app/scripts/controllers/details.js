'use strict';

(function () {

  var dependencies = ['$scope', '$routeParams', 'state'];
  var Ctrl = function ($scope, $routeParams, state) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    this.fetchDetails();
  };

  Ctrl.prototype.fetchDetails = function(){
    if(this.state.scan && this.state.scan.results){
      this.details = this.state.scan.results[this.$routeParams.file];
    } else {
      this.state.newScan(this.$routeParams.scan);
      this.state.scan.getResults().then(function(){
        this.details = this.state.scan.results[this.$routeParams.file];
      }.bind(this));
    }
  };

  Ctrl.$inject = dependencies;
  angular.module('irma').controller('DetailsCtrl', Ctrl);
}());