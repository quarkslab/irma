'use strict';

(function () {

  var dependencies = ['$http', '$q'];
  var Bridge = function ($http, $q) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    this.rootUrl = 'http://frontend.irma.qb/_api';

    this.get = function(options){
      var deferred = $q.defer();

      $http.get(this.rootUrl+options.url, {params: options.payload}).then(function(data){
        deferred.resolve(data.data);
      },function(data){
        deferred.reject(data.data);
      });
      return deferred.promise;
    };

    this.post = function(options){
      var deferred = $q.defer();

      $http.post(this.rootUrl+options.url, options.payload).then(function(data){
        deferred.resolve(data.data);
      },function(data){
        deferred.reject(data.data);
      });
      return deferred.promise;
    };

  };

  Bridge.$inject = dependencies;
  angular.module('irma').service('bridge', Bridge);
}());