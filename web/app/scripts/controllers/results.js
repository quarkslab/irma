(function () {
  'use strict';

  angular
    .module('irma')
    .controller('ResultsCtrl', Results);

  Results.$inject = ['$scope', '$routeParams', 'state'];

  function Results($scope, $routeParams, state) {
    var vm = this;
    vm.newScan = newScan;

    activate();

    function activate() {
      if (state.status !== 'results') {
        state.newScan($routeParams.scan);
        state.scan.getResults();
      }
    }

    function newScan() {
      state.newScan();
      state.goTo('selection');
    }
  }
}) ();
