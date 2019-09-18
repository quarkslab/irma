(function () {
  angular
    .module('irma')
    .config(configure);

  function configure($routeProvider, $locationProvider) {
    $locationProvider.html5Mode(true);

    $routeProvider
      .when('/selection', {
        templateUrl: '/views/selection.html',
        controller: 'SelectionCtrl',
        controllerAs: 'vm',
        location: 'selection',
      })
      .when('/scan/:scan', {
        templateUrl: '/views/scan.html',
        controller: 'ScanCtrl',
        controllerAs: 'vm',
        location: 'scan',
      })
      .when('/results/:resultId', {
        templateUrl: '/views/details.html',
        controller: 'DetailsCtrl',
        controllerAs: 'vm',
        location: 'results',
      })
      .when('/search', {
        templateUrl: '/views/search.html',
        controller: 'SearchCtrl',
        controllerAs: 'vm',
        location: 'search',
        /**
         * This prevent the page to reload when `$location.search` function is call to modify URL
         * query string parameters
         */
        reloadOnSearch: false,
        resolve: {
          tagPrepService: ['resultsManager', function (resultsManager) {
            return resultsManager.getAvailableTags();
          }],
        },
      })
      .when('/maintenance', {
        templateUrl: '/views/maintenance.html',
        controller: 'MaintenanceCtrl',
        controllerAs: 'vm',
      })
      .otherwise({ redirectTo: '/selection' });
  }
}());
