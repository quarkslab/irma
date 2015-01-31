'use strict';

angular.module('irma', [
  'ngResource',
  'ngSanitize',
  'ngRoute',
  'angularFileUpload',
  'mgcrea.ngStrap',
  'mgcrea.ngStrap.helpers.dimensions',
  'ngJsonExplorer',
  'angular-capitalize-filter',
  'angularMoment',
  'ngTable',
  'angular-svg-round-progress'
])
  .constant('constants', {
    fakeDelay: 0,
    baseApi: '/_api',
    speed: 1500,
    refresh: 1000,
    forceScanDefault: true,
    scanStatusCodes: {
      STOPPED: 0,
      RUNNING: 1,
      FINISHED: 2
    }
  })
  .constant('angularMomentConfig', {
    preprocess: 'unix'
  })
  .config(['$routeProvider', '$locationProvider', function ($routeProvider, $locationProvider) {
    $locationProvider.html5Mode(true);

    $routeProvider
      .when('/selection', {
        templateUrl: '/views/selection.html',
        controller: 'SelectionCtrl',
        controllerAs: 'vm',
        location: 'selection',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })
      .when('/upload', {
        templateUrl: '/views/upload.html',
        controller: 'UploadCtrl',
        location: 'upload',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })
      .when('/scan/:scan', {
        templateUrl: '/views/scan.html',
        controller: 'ScanCtrl',
        controllerAs: 'vm',
        location: 'scan',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })
      .when('/scan/:scanId/file/:fileIdx', {
        templateUrl: '/views/details.html',
        controller: 'DetailsCtrl',
        controllerAs: 'vm',
        location: 'results',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })
      .when('/search', {
        templateUrl: '/views/search.html',
        controller: 'SearchCtrl',
        controllerAs: 'vm',
        location: 'search',
        resolve: {
          maintenance: ['state', function(state){ return state.pingApi();}]
        }
      })
      .when('/maintenance',
       {
        templateUrl: '/views/maintenance.html',
        controller: 'MaintenanceCtrl',
        resolve: {
          maintenance: ['state', function(state){ return state.noPingApi();}]
        }
      })
      .otherwise({ redirectTo: '/selection' });
  }])
  .run(['$window', '$rootScope', '$location', '$anchorScroll', function($window, $rootScope, $location, $anchorScroll) {

    var bodyElement = angular.element($window.document.body);
    var targetElement = bodyElement;

    targetElement.on('click', function(evt) {
      var el = angular.element(evt.target);
      var hash = el.attr('href');

      if(!hash || hash[0] !== '#') { return; }
      if(hash.length > 1 && hash[1] === '/') { return; }
      if(evt.which !== 1) { return; }

      evt.preventDefault();

      $location.hash(hash.substr(1));
      $anchorScroll();
    });

    setTimeout(function() {
      $anchorScroll();
    }, 0);
  }]);
