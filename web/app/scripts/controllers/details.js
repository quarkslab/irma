(function () {
  'use strict';

  angular
    .module('irma')
    .controller('DetailsCtrl', Details);

  Details.$inject = ['$rootScope', '$scope', '$routeParams', 'state', 'resultsManager'];

  function Details($rootScope, $scope, $routeParams, state, resultManager) {
    var vm = this;
    vm.result = undefined;
    vm.filterByProbeType = filterByProbeType;

    activate();

    function activate() {
      fetchDetails();
    }

    function fetchDetails() {
      if(!state.scan) {
        state.newScan($routeParams.scanId);
      }

      resultManager.getResult($routeParams.scanId, $routeParams.resultId).then(function(result) {
        vm.result = result;
      });
    }

    function filterByProbeType(items) {
      var result = {};

      angular.forEach(items, function(value, key) {
        if (key !== 'antivirus') {
          result[key] = value;
        }
      });

      return result;
    }
  }
}) ();
