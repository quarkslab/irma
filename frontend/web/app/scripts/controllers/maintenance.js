'use strict';

(function () {

  var dependencies = ['$scope', 'state'];
  var Ctrl = function ($scope, state) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    // We can do things here
  };

  Ctrl.$inject = dependencies;
  angular.module('irma').controller('MaintenanceCtrl', Ctrl);
}());