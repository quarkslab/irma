(function () {
  angular
    .module('irma')
    .controller('SelectionCtrl', Selection);

  function Selection($scope, alerts, state) {
    // Exports
    angular.extend(this, { start });

    // IIFE when entering the controller
    (function run() {
      state.newUploader();
    }());

    // Functions
    function start() {
      if (state.noActiveProbes()) {
        alerts.add('<strong>Error:</strong> There is no probe available.', 'danger');
      } else {
        angular.extend(state, { lastAction: 'startScan' });
        $scope.$emit('startScan');
      }
    }
  }
}());
