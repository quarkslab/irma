(function () {
  'use strict';

  angular
    .module('irma')
    .controller('ScanCtrl', Scan);

  Scan.$inject = ['$scope', '$routeParams', '$location', 'state', 'constants'];

  function Scan($scope, $routeParams, $location, state, constants) {
    var vm = this;
    vm.scanStatusCodes = constants.scanStatusCodes;
    vm.cancel = cancel;
    vm.newScan = newScan;
    vm.csvReportURI = undefined;
    vm.getLabelByFileStatus = getLabelByFileStatus;

    activate();

    function activate() {
      if(state.status !== 'scan' || state.scan === undefined || state.scan.id !== $routeParams.scan) {
        state.newScan($routeParams.scan);
      }

      state.scan.updateScan();

      vm.csvReportURI = constants.baseApi + '/scans/' + state.scan.id + '/report';
    }

    function cancel() {
      state.lastAction = 'cancelScan';
      $scope.$emit('cancelScan');
    }

    function newScan() {
      state.newScan();
      state.goTo('selection');
    }

    function getLabelByFileStatus(status)
    {
      var label;

      switch(status){
          case null:
              label = 'label-info';
              break;
          case 0:
              label =  'label-success';
              break;
          case 1:
              label =  'label-danger';
              break;
          default:
              label =  'label-warning';
       }
      return label;
    }

    $scope.$on('$destroy', function(){
      state.scan.stopUpdate();
    });
  }
}) ();
