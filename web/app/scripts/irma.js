'use strict';

angular.module('irma', [
  'ngResource',
  'ngSanitize',
  'ngRoute',
  'angularFileUpload',
  'mgcrea.ngStrap',
  'gd.ui.jsonexplorer',
  'angular-capitalize-filter'
])
  .constant('constants', {
    fakeDelay: 0,
    baseApi: '/_api',
    speed: 1500,
    refresh: 1000,
    forceScanDefault: true,
    scanStatusCodes: {
      STOPPED: 0,
      STARTED: 1,
      FINISHED: 2
    }
  })
  .config(['$routeProvider', function ($routeProvider) {

    $routeProvider
      .when('/selection', {
        templateUrl: 'views/selection.html',
        controller: 'SelectionCtrl',
        controllerAs: 'vm',
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
      .when('/scan/:scan', {
        templateUrl: 'views/scan.html',
        controller: 'ScanCtrl',
        controllerAs: 'vm',
        location: 'scan',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })
      .when('/scan/:scanId/file/:resultId', {
        templateUrl: 'views/details.html',
        controller: 'DetailsCtrl',
        controllerAs: 'vm',
        location: 'results',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })
      .when('/search', {
        templateUrl: 'views/existing.html',
        controller: 'ExistingCtrl',
        location: 'search',
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
