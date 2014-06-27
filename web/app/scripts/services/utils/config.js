'use strict';

(function () {

  var dependencies = ['bridge'];
  var Config = function (bridge) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    this.getProbes = function(){
      return bridge.get({url: '/probe/list'});
    };

  };

  Config.$inject = dependencies;
  angular.module('irma').service('config', Config);
}());