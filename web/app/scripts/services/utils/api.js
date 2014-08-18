'use strict';

(function () {

  var dependencies = ['$q', 'bridge'];
  var API = function ($q, bridge) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    this.ping =       function(){                 return bridge.get({url: '/probe/list', noAlerts: true}); };
    this.getProbes =  function(){                 return bridge.get({url: '/probe/list'}); };

    this.scan = {
      getNewId:       function() {                 return bridge.get({url: '/scan/new'}); },
      launch:         function(scan, params) {     return bridge.get({url: '/scan/launch/'+scan.id, payload: params}); },
      cancel:         function(scan) {             return bridge.get({url: '/scan/cancel/'+scan.id}); },
      getProgress:    function(scan) {             return bridge.get({url: '/scan/progress/'+scan.id}); }, 
      getResults:     function(scan) {             return bridge.get({url: '/scan/result/'+scan.id}); },

      // Returns an url
      getAddUrl:      function(scan){              return bridge.rootUrl+'/scan/add/'+scan.id; }
    };
  };

  API.$inject = dependencies;
  angular.module('irma').service('api', API);
}());
