'use strict';

var apiRoot = 'http://frontend.irma.qb/_api';

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
