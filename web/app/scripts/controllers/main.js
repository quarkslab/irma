'use strict';

angular.module('irma')
.controller('MainCtrl', function ($scope, $timeout, $http, $fileUploader) {

  $scope.context = 'selection';
  $scope.scanId = null;
  $scope.rootApi = apiRoot;
  $scope.currentProcess = null;
  $scope.settings = {
    probes: [],
    force: false
  };
  $scope.advancedSettings = false;

  var uploader = $scope.uploader = $fileUploader.create(),
    speed = 1000;

  $scope.loadProbes = function(){
    $http.get($scope.rootApi+'/probe/list').then(function(response){
      if(response.data.code === 0){
        for(var i=0; i<response.data.probe_list.length; i++){
          $scope.settings.probes.push({name: response.data.probe_list[i], active: true});
        }
      } else {
        console.error('Error occured retrieving probe list');
      }
    });
  };
  $scope.toggleAdvanced = function(force){
    $scope.advancedSettings = (force !== null)? force: !$scope.advancedSettings;
  };

  $scope.uploadFiles = function(){
    if(!uploader.getNotUploadedItems().length)
      return false;

    // Get a scan id
    $http.get($scope.rootApi+'/scan/new').then(function(response){

      if(response.data.code === 0){
        $scope.scanId = response.data.scan_id;

        $scope.context = 'upload';
        _.each(uploader.getNotUploadedItems(), function(item){
          item.url = $scope.rootApi+'/scan/add/'+$scope.scanId;
        });
        uploader.uploadAll();
      } else {
        console.error('Error occured when asking for a new scan');
      }
    });
  };
  $scope.cancelUpload = function(){
    $scope.context = 'selection';
    uploader.cancelAll();
  };


  uploader.bind('progressall', function (event, progress) {
    console.info('Total progress: ' + progress);
  });
  uploader.bind('completeall', function (event, items) {
    // Check if all files were successfully uploaded
    var allGood = true;
    _.each(uploader.queue, function(item){
      if(!item.isSuccess) allGood = false;
    });

    if(allGood)
      // Asks for the scan to begin
      $scope.currentProcess = $timeout(function(){

        var probes = [], hasInactive = false;
        for(var i=0; i<$scope.settings.probes.length; i++){
          if($scope.settings.probes[i].active)
            probes.push($scope.settings.probes[i].name)
          else
            hasInactive = true;
        }
        var params = {params: {}};
        if(hasInactive)
          params.params.probe = probes.join(',');
        if($scope.settings.force)
          params.params.force = true;

        console.log(params);

        $http.get($scope.rootApi+'/scan/launch/'+$scope.scanId, params).then(function(response){

          $scope.results = {};
          if(response.data.code === 0){
            $scope.scanDisplay();
          } else {
            console.error('Error occured during scan launch');
          }
        });
      }, speed);
    else
      console.error('Error occured during upload');
  });


  $scope.scanDisplay = function(){
  
    $scope.abort = function(){
      $http.get($scope.rootApi+'/scan/cancel/'+$scope.scanId);
      $timeout.cancel($scope.currentProcess);
      $scope.progress = 0;
      uploader.clearQueue();
      $scope.context = 'selection';
    };

    $scope.progress = 0;
    $scope.context = 'scan';
    $scope.currentProcess = $timeout($scope.updateScan, speed);
  };

  $scope.updateScan = function(){
    $http.get($scope.rootApi+'/scan/progress/'+$scope.scanId).then(function(response){




      if(response.data.code === 0){

        $scope.progress = Math.round(response.data.progress_details.finished / response.data.progress_details.total *100);
        $scope.currentProcess = $timeout($scope.updateScan, speed);
        $scope.fetchResults();

      } else if(response.data.code === 1){
        $scope.progress = 100;

        if(response.data.msg == 'finished')
          $scope.resultsDisplay();
        else
          $scope.currentProcess = $timeout($scope.updateScan, speed);
      } else
        console.error('Error occured during scan');
    });
  };


  $scope.fetchResults = function(fn){
    var task = $http.get($scope.rootApi+'/scan/result/'+$scope.scanId).then(function(response){
      if(response.data.code === 0){
        $scope.results = response.data.scan_results;
      } else
        console.error('Error occured retrieving results');
    });
    return task;
  };
  $scope.resultsDisplay = function(){
    $scope.fetchResults().then(function(){ $scope.context = 'results';});
  };

  // Initialization
  $scope.loadProbes();

});
