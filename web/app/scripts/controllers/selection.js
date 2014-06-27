'use strict';

(function () {

  var dependencies = ['$scope', '$location', 'alerts', 'state', 'config', 'constants', 'ScanModel'];
  var Ctrl = function ($scope, $location, alerts, state, config, constants, Scan) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    //if(this.state.initRequired()){
      // Init scan
      this.init();
      this.state.currentScan = new Scan();
    //}

    // Bind things to scope
    $scope.scan = this.state.currentScan;
    $scope.trigger = this.trigger.bind(this);
    $scope.toggleProbe = this.toggleProbe.bind(this);
    $scope.goToScan = this.goToScan.bind(this);
  };

  Ctrl.prototype.init = function(){

    this.$scope.settings = {
      display: false,
      force: this.constants.forceScanDefault,
      probes: [],
      nbActiveProbes: 0
    };
    this.state.settings = this.$scope.settings;

    var disabledProbes = ['VirusTotal'];

    this.config.getProbes().then(function(data){
      for(var i=0; i<data.probe_list.length; i++){
        if(disabledProbes.indexOf(data.probe_list[i]) === -1){
          this.$scope.settings.probes.push({name: data.probe_list[i], active: true});
        } else {
          this.$scope.settings.probes.push({name: data.probe_list[i], active: false});
        }
      }
      this.$scope.settings.nbActiveProbes = this.$scope.settings.probes.length;
    }.bind(this), function(){
      this.alerts.add({standard: 'probesListError'});
    }.bind(this));
  };

  Ctrl.prototype.trigger = function(){
    this.state.trigger('startUpload');

    if(this.$scope.settings.nbActiveProbes < 1){
      this.alerts.add({standard: 'noSelectedProbes'});
    } else {
      this.$scope.scan.uploadFiles().then(function(id){
        this.alerts.add({standard: 'uploadStarted'});
        this.state.initResults(this.$scope.settings);
        this.$location.path('/upload');
      }.bind(this), function(error){
        this.alerts.add({standard: error});
      }.bind(this));
    }
  };

  Ctrl.prototype.goToScan = function(id){
    this.state.trigger('goToResults');

    this.$location.path('/results/'+id);
  };

  Ctrl.prototype.toggleProbe = function(probe){
    this.$scope.settings.nbActiveProbes += (probe.active)? -1: 1;
    probe.active = !probe.active;
  };

  Ctrl.$inject = dependencies;
  angular.module('irma').controller('SelectionCtrl', Ctrl);
}());