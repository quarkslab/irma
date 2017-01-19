(function () {
  'use strict';

  angular
    .module('irma')
    .controller('SearchCtrl', Search);

  Search.$inject = ['$scope', 'ngTableParams', 'dataservice', 'alerts', 'resultsManager'];

  function Search($scope, ngTableParams, dataservice, alerts, resultManager) {
    var vm = this;
    // Search params/models passed to the view
    vm.searchedTags = undefined;
    vm.searchedPreviousTags = undefined;
    vm.searchedStr = '';
    vm.searchedPreviousStr = undefined;
    vm.searchedType = "name";
    vm.tableParams = new ngTableParams({
      page: 1,            // show first page
      count: 25           // count per page
    }, {
      total: 0,
      getData: getData
    });
    
    $scope.availableTags = undefined;
    
    $scope.loadAvailableTags = function(query) {
        var results = [];
        for(var i=0; i < $scope.availableTags.length; i++) {
            if($scope.availableTags[i].text.toLowerCase().indexOf(query.toLowerCase()) > -1) {
                results.push($scope.availableTags[i]);
            }
        }
        return results;
    };
     
    activate();

    function activate() {
    	fetchAvailableTags();
    }
    
    function fetchAvailableTags() {    
    	resultManager.getAvailableTags().then(function(results) {
    		$scope.availableTags = results.items;
		});
	}

    function getData($defer, params) {
    	alerts.removeAll();

	    if (vm.searchedStr !== vm.searchedPreviousStr || vm.searchedTags !== vm.searchedPreviousTags) {
	      vm.searchedPreviousStr = vm.searchedStr;
	      vm.searchedPreviousTags = vm.searchedTags;
	      params.page(1);
	    }
	
	    dataservice.searchFiles(vm.searchedTags, vm.searchedType, vm.searchedStr, (params.page() - 1)* params.count(), params.count()).then(function(data) {
	      params.total(data.total);
	      $defer.resolve(data.items);
	    });
    }
  }
}) ();
