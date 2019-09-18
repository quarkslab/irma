(function () {
  angular
    .module('irma')
    .controller('ResultsCtrl', Results);

  function Results($routeParams, state) {
    // Exports
    angular.extend(this, { newScan });

    // IIFE when entering the controller
    (function run() {
      if (state.status !== 'results') {
        state.newScan($routeParams.scan);
        state.scan.getResults();
      }
    }());

    // Functions
    function newScan() {
      state.newScan();
      state.goTo('selection');
    }
  }
}());
