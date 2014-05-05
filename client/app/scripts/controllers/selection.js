'use strict';

(function () {

  var dependencies = ['$scope', '$location', 'alerts', 'state', 'config', 'ScanModel'];
  var Ctrl = function ($scope, $location, alerts, state, config, Scan) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    // Init controller
    this.init();

    // Creates new scan
    this.state.currentScan = new Scan();

    // Bind things to scope
    $scope.scan = this.state.currentScan;
    $scope.trigger = this.trigger.bind(this);
    $scope.goToScan = this.goToScan.bind(this);
  };

  Ctrl.prototype.init = function(){

    this.$scope.settings = {
      display: false,
      force: true,
      probes: []
    };
    this.state.settings = this.$scope.settings;

    this.config.getProbes().then(function(data){
      if(!data.probe_list || data.probe_list.length === 0){ data.probe_list = ['Probe1', 'Probe2', 'Probe3'];}

      for(var i=0; i<data.probe_list.length; i++){
        this.$scope.settings.probes.push({name: data.probe_list[i], active: true});
      }
    }.bind(this), function(){
      this.alerts.add({standard: 'probesListError'});
    }.bind(this));
  };

  Ctrl.prototype.trigger = function(){
    this.$scope.scan.uploadFiles().then(function(id){
      this.alerts.add({standard: 'uploadStarted'});
      this.state.initResults(this.$scope.settings);
      this.$location.path('/upload');
    }.bind(this), function(error){
      this.alerts.add({standard: error});
    }.bind(this));
  };

  Ctrl.prototype.goToScan = function(id){
    this.$location.path('/results/'+id);
  };

  Ctrl.$inject = dependencies;
  angular.module('irma').controller('SelectionCtrl', Ctrl);
}());