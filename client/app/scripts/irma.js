'use strict';

angular.module('irma', [
  'ngResource',
  'ngSanitize',
  'ngRoute',
  'angularFileUpload'
])
  .constant('constants', {
    useMocks: true,
    fakeDelay: 500,
    baseApi: '/api',
    speed: 1000
  })
  .config(['$routeProvider', function ($routeProvider) {

    $routeProvider
      .when('/selection',   {templateUrl: 'views/selection.html',     controller: 'SelectionCtrl',    location: 'selection'})
      .when('/upload',      {templateUrl: 'views/upload.html',        controller: 'UploadCtrl',       location: 'upload'})
      .when('/scan',        {templateUrl: 'views/scan.html',          controller: 'ScanCtrl',         location: 'scan'})
      .when('/results',     {templateUrl: 'views/results.html',       controller: 'ResultsCtrl',      location: 'results'})
      .otherwise({ redirectTo: '/selection' });
  }]);