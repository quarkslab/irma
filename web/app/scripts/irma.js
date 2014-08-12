'use strict';

angular.module('irma', [
  'ngResource',
  'ngSanitize',
  'ngRoute',
  'angularFileUpload',
  'mgcrea.ngStrap'
])
  .constant('constants', {
    fakeDelay: 0,
    baseApi: 'http://frontend.irma.qb/_api',
    speed: 1500,
    refresh: 1000,
    forceScanDefault: true
  })
  .config(['$routeProvider', function ($routeProvider) {

    $routeProvider
      .when('/selection', {
        templateUrl: 'views/selection.html',
        controller: 'SelectionCtrl',
        location: 'selection',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })
      .when('/upload', {
        templateUrl: 'views/upload.html',
        controller: 'UploadCtrl',
        location: 'upload',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })
      .when('/scan', {
        templateUrl: 'views/scan.html',
        controller: 'ScanCtrl',
        location: 'scan',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })
      .when('/results', {
        templateUrl: 'views/existing.html',
        controller: 'ExistingCtrl',
        location: 'results',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })
      .when('/results/:scan', {
        templateUrl: 'views/results.html',
        controller: 'ResultsCtrl',
        location: 'results',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })
      .when('/results/:scan/file/:file', {
        templateUrl: 'views/details.html',
        controller: 'DetailsCtrl',
        controllerAs: 'detailsCtrl',
        location: 'results',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })

      .when('/maintenance',
       {
        templateUrl: 'views/maintenance.html',
        controller: 'MaintenanceCtrl',
        resolve: {
          maintenance: ['state', function(state){ return state.noPingApi();}]
        }
      })

      .otherwise({ redirectTo: '/selection' });
  }]);
