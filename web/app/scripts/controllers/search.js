(function () {
  'use strict';

  angular
    .module('irma')
    .controller('SearchCtrl', Search);

  Search.$inject = ['$scope', 'state'];

  function Search($scope, state) {
    var vm = this;
    vm.goToScan = goToScan;

    function goToScan(id) {
      state.goTo('scan', id);
    }
  }
}) ();
