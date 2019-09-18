(function () {
  angular
    .module('irma')
    .controller('ScanCtrl', Scan);

  function Scan($scope, $routeParams, $location, state, constants) {
    // Exports
    const vm = this;
    angular.extend(vm, {
      // Variables
      csvReportURI: undefined,
      scanStatusCodes: constants.scanStatusCodes,

      // Functions
      cancel,
      newScan,
      getLabelByFileStatus,
    });

    // IIFE when entering the controller
    (function run() {
      $scope.$on('$destroy', () => {
        state.scan.stopUpdate();
      });

      if (state.status !== 'scan' || state.scan === undefined || state.scan.id !== $routeParams.scan) {
        state.newScan($routeParams.scan);
      }

      state.scan.updateScan();

      vm.csvReportURI = `${constants.baseApi}/scans/${state.scan.id}/report`;
    }());

    // Functions
    function cancel() {
      angular.extend(state, {
        lastAction: 'cancelScan',
      });
      $scope.$emit('cancelScan');
    }

    function newScan() {
      state.newScan();
      state.goTo('selection');
    }

    function getLabelByFileStatus(status) {
      let label;

      switch (status) {
        case null:
          label = 'label-info';
          break;
        case 0:
          label = 'label-success';
          break;
        case 1:
          label = 'label-danger';
          break;
        default:
          label = 'label-warning';
      }
      return label;
    }
  }
}());
