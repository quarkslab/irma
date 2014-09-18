'use strict';

(function () {

  var dependencies = ['$http', '$q', '$timeout', 'alerts', 'constants'];
  var Bridge = function ($http, $q, $timeout, alerts, constants) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    this.rootUrl = constants.baseApi;

    this.get = function(options){
      var deferred = $q.defer();

      $http.get(this.rootUrl+options.url, {params: options.payload}).then(function(data){
        if(data.data.code === -1){
          $timeout(function(){
            if(!options.noAlerts){ this.alerts.add({standard: 'apiErrorWithMsg', apiMsg: data.data.msg});}
            deferred.reject(data.data);
          }.bind(this), constants.fakeDelay);
        } else {
          $timeout(function(){
            deferred.resolve(data.data);
          }, constants.fakeDelay);
        }
      }.bind(this), function(data){
        if(!options.noAlerts){ this.alerts.add({standard: 'apiError'});}
        $timeout(function(){ deferred.reject(data.data); }, constants.fakeDelay);
      }.bind(this));

      return deferred.promise;
    };

    this.post = function(options){
      var deferred = $q.defer();

      $http.post(this.rootUrl+options.url, options.payload).then(function(data){
        if(data.data.code !== 0){
          $timeout(function(){ deferred.reject(data.data); }, constants.fakeDelay);
        } else {
          $timeout(function(){ deferred.resolve(data.data); }, constants.fakeDelay);
        }
      }.bind(this), function(data){
        if(!options.noAlerts){ this.alerts.add({standard: 'apiError'});}
        $timeout(function(){ deferred.reject(data.data); }, constants.fakeDelay);
      });
      return deferred.promise;
    };

  };

  Bridge.$inject = dependencies;
  angular.module('irma').service('bridge', Bridge);
}());
