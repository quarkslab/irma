(function () {
  'use strict';

  angular
    .module('irma')
    .controller('SearchCtrl', Search);

  Search.$inject = ['ngTableParams', 'dataservice', 'alerts'];

  function Search(ngTableParams, dataservice, alerts) {
    var vm = this;
    // Search params/models passed to the view
    vm.searchedStr = undefined;
    vm.searchedPreviousStr = undefined;
    vm.searchedType = "name";
    vm.tableParams = new ngTableParams({
      page: 1,            // show first page
      count: 25           // count per page
    }, {
      total: 0,
      getData: getData
    });

    function getData($defer, params) {
      alerts.removeAll();

      if (typeof vm.searchedStr === 'undefined') {
        $defer.resolve([]);
      } else {
        if (vm.searchedStr !== vm.searchedPreviousStr) {
          vm.searchedPreviousStr = vm.searchedStr;
          params.page(1);
        }

        dataservice.searchFiles(vm.searchedType, vm.searchedStr, params.page(), params.count()).then(function(data) {
          params.total(data.total);
          $defer.resolve(data.items);
        });
      }
    }
  }
}) ();
