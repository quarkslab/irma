'use strict';

(function () {

  var dependencies = ['$scope', '$location', '$timeout', 'constants', 'alerts', 'state', 'config', 'ScanModel'];
  var Ctrl = function ($scope, $location, $timeout, constants, alerts, state, config, Scan) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    // If no current scan is set, we reset the route to the selection
    if(!this.state.currentScan){ return this.$location.path('/');}

    // Scope bindings
    $scope.scan = this.state.currentScan;
    $scope.cancel = this.cancelUpload.bind(this);

    // Scope events;
    $scope.$on('uploadComplete', function(event, data){
      if(data.status){
        this.alerts.add({standard: 'uploadComplete'});
        this.state.upgradeResults(data.files);
        $timeout(function(){
          this.$location.path('/scan');
        }.bind(this), constants.speed);
      } else {
        this.alerts.add({standard: 'errorInUpload'});
        this.$location.path('/');
      }
    }.bind(this));


    // Launch upload
    $timeout(function(){
      this.state.currentScan.uploader.uploadAll();
    }.bind(this), constants.speed);
  };

  Ctrl.prototype.cancelUpload = function(){
    this.state.trigger('cancelUpload');
    this.state.currentScan.cancelUpload();
    this.alerts.add({standard: 'uploadCanceled'});
    this.$location.path('/');
  };

  Ctrl.$inject = dependencies;
  angular.module('irma').controller('UploadCtrl', Ctrl);
}());