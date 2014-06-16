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
    baseApi: '/_api',
    speed: 1000,
    forceScanDefault: true
  })
  .config(['$routeProvider', function ($routeProvider) {

    $routeProvider
      .when('/selection',         {templateUrl: 'views/selection.html',     controller: 'SelectionCtrl',    location: 'selection'})
      .when('/upload',            {templateUrl: 'views/upload.html',        controller: 'UploadCtrl',       location: 'upload'})
      .when('/scan',              {templateUrl: 'views/scan.html',          controller: 'ScanCtrl',         location: 'scan'})
      .when('/results',           {templateUrl: 'views/existing.html',      controller: 'ExistingCtrl',     location: 'results'})
      .when('/results/:scan',     {templateUrl: 'views/results.html',       controller: 'ResultsCtrl',      location: 'results'})
      .otherwise({ redirectTo: '/selection' });
  }]);
