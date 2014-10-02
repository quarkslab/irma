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

      $http.get(vm.rootUrl + options.url, {params: options.payload}).then(function(data) {
        if(data.data.code === -1) {
          $timeout(function() {
            if(!options.noAlerts){ alerts.add({standard: 'apiErrorWithMsg', apiMsg: data.data.msg});}
            deferred.reject(data.data);
          }, constants.fakeDelay);
        } else {
          $timeout(function() {
            deferred.resolve(data.data);
          }, constants.fakeDelay);
        }
      }, function(data) {
        if(!options.noAlerts) { alerts.add({standard: 'apiError'});}
        $timeout(function() { deferred.reject(data.data); }, constants.fakeDelay);
      });

      return deferred.promise;
    }

    function post(options){
      var deferred = $q.defer();

      $http.post(vm.rootUrl+options.url, options.payload).then(function(data) {
        if(data.data.code !== 0) {
          $timeout(function(){ deferred.reject(data.data); }, constants.fakeDelay);
        } else {
          $timeout(function(){ deferred.resolve(data.data); }, constants.fakeDelay);
        }
      }, function(data) {
        if(!options.noAlerts) { alerts.add({standard: 'apiError'});}
        $timeout(function() { deferred.reject(data.data); }, constants.fakeDelay);
      });
      return deferred.promise;
    }
  }
}) ();
