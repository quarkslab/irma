'use strict';

var apiRoot = '/_api';

angular.module('irma', [
  'ngCookies',
  'ngResource',
  'ngSanitize',
  'ngRoute',
  'angularFileUpload'
])
.config(function ($routeProvider) {
  $routeProvider
  .when('/', { templateUrl: 'views/main.html', controller: 'MainCtrl'})
  .otherwise({ redirectTo: '/'});
});
