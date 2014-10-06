(function () {
  'use strict';

  angular
    .module('irma')
    .controller('DetailsCtrl', Details);

  Details.$inject = ['$rootScope', '$scope', '$routeParams', 'state', 'resultsManager'];

  function Details($rootScope, $scope, $routeParams, state, resultManager) {
    var vm = this;
    vm.results = undefined;

    activate();

    function activate() {
      fetchDetails();
    }

    function fetchDetails() {
      if(!state.scan) {
        state.newScan($routeParams.scanId);
      }

      resultManager.getResult($routeParams.scanId, $routeParams.resultId).then(function(results) {
        vm.results = results;
      });
    }
  }
}) ();
