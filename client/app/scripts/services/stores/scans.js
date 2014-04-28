'use strict';

(function () {

  var dependencies = ['bridge', 'state'];
  var ScanStore = function (bridge, state) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    // API endpoints
    this.getNewId = function(){
      return bridge.get({url: '/scan/new'});
    };

    this.getAddUrl = function(id){
      return bridge.rootUrl+'/scan/add/'+id;
    };

    this.launchScan = function(){

      var probes = [], hasInactive = false;
      for(var i=0; i<this.state.settings.probes.length; i++){
        if(this.state.settings.probes[i].active){
          probes.push(this.state.settings.probes[i].name)
        } else {
          hasInactive = true;
        }
      }
      var params = {};
      if(hasInactive)
        params.probe = probes.join(',');
      if(this.state.settings.force)
        params.force = true;

      return bridge.get({url: '/scan/launch/'+this.state.currentScan.id, payload: params});
    };

    this.cancelScan = function(){
      return bridge.get({url: '/scan/cancel/'+this.state.currentScan.id});
    }

  };

  ScanStore.$inject = dependencies;
  angular.module('irma').service('scanStore', ScanStore);
}());