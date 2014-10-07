(function () {
  'use strict';

  angular
    .module('irma')
    .controller('ScanCtrl', Scan);

  Scan.$inject = ['$scope', '$routeParams', '$location', 'state', 'constants'];

  function Scan($scope, $routeParams, $location, state, constants) {
    var vm = this;
    vm.scanStatusCodes = constants.scanStatusCodes;
    vm.scanUrl = $location.path();
    vm.cancel = cancel;
    vm.newScan = newScan;

    activate();

    function activate() {
      if(state.status !== 'scan' || state.scan === undefined || state.scan.id !== $routeParams.scan) {
        state.newScan($routeParams.scan);
        state.scan.updateScan();
      }
    }

    function cancel() {
      state.lastAction = 'cancelScan';
      $scope.$emit('cancelScan');
    }

    function newScan() {
      state.newScan();
      state.goTo('selection');
    }
  }
}) ();
