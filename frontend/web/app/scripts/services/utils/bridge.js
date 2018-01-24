(function () {
  'use strict';

  Bridge.$inject = ['$http', '$q', '$timeout', 'alerts', 'constants'];
  angular.module('irma').service('bridge', Bridge);

  function Bridge($http, $q, $timeout, alerts, constants) {
    var vm = this;
    vm.rootUrl = constants.baseApi;
    // Function binding
    vm.get = get;
    vm.post = post;

    function get(options) {
      var deferred = $q.defer();

      $http.get(vm.rootUrl + options.url, {params: options.payload}).then(function(response) {
        $timeout(function() {
          deferred.resolve(response.data);
        }, constants.fakeDelay);
      }, function(response) {
        // In case of error with the API
        if(!options.noAlerts) {
          alerts.add({
            standard: 'apiErrorWithMsg',
            apiMsg: response.data.errors || {},
          });
        }
        $timeout(function() { deferred.reject(response.data); }, constants.fakeDelay);
      });

      return deferred.promise;
    }

    function post(options){
      var deferred = $q.defer();

      $http.post(vm.rootUrl+options.url, options.payload).then(function(response) {
          $timeout(function(){ deferred.resolve(response.data); }, constants.fakeDelay);
      }, function(response) {
        // In case of error with the API
        if(!options.noAlerts) {
          alerts.add({
            standard: 'apiErrorWithMsg',
            apiMsg: response.data.errors || {},
          });
        }
        $timeout(function() { deferred.reject(response.data); }, constants.fakeDelay);
      });

      return deferred.promise;
    }
  }
}) ();
