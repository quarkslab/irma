(function () {
  'use strict';

  angular
    .module('irma')
    .controller('SelectionCtrl', Selection);

  Selection.$inject = ['$scope', 'alerts', 'state'];

  function Selection($scope, alerts, state) {
    var vm = this;
    vm.start = start;

    activate();

    function activate() {
      state.newScan();
    }

    function start() {
      if(state.noActiveProbes()) {
        alerts.add({standard: 'noProbes'});
      } else {
        state.lastAction = 'startUpload';
        $scope.$emit('startUpload');
      }
    }
  }
}) ();
