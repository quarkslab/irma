(function () {
  'use strict';

  angular
    .module('irma')
    .controller('DetailsCtrl', Details);

  Details.$inject = ['$rootScope', '$scope', '$routeParams', 'state', 'resultsManager', 'api'];

  function Details($rootScope, $scope, $routeParams, state, resultManager, api) {
    var vm = this;
    vm.results = undefined;    
    $scope.tags = undefined;
    $scope.availableTags = undefined;
    
    $scope.tagAdded = function(tag) {
    	api.tag.addTag(vm.results.file_infos.sha256, tag.id);
    };
    
    $scope.tagRemoved = function(tag) {
    	api.tag.removeTag(vm.results.file_infos.sha256, tag.id);
    };
    
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
      fetchDetails();
    }

    function fetchDetails() {
      if(!state.scan) {
        state.newScan($routeParams.scanId);
      }

      resultManager.getResult($routeParams.resultId).then(function(results) {
        vm.results = results;
        $scope.tags = results.file_infos.tags;
      });
      
      resultManager.getAvailableTags().then(function(results) {
    	  $scope.availableTags = results.items;
        });
    }
  }
}) ();
