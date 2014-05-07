'use strict';

/*
 *  SCAN MODEL
 */
(function () {

  var dependencies = ['$rootScope', '$fileUploader', '$q', '$timeout', 'constants', 'scanStore'];
  var Scan = function ($rootScope, $fileUploader, $q, $timeout, constants, scanStore) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}

    var ScanModel = function(options, flag){
      this.id = undefined;
      this.store = scanStore;
      this.uploader = $fileUploader.create();
      this.task = null;
      this.baseResults = null;

      this.uploader.bind('completeall', this.uploadComplete.bind(this));
    };

    ScanModel.prototype.uploadFiles = function(next){
      var deferred = $q.defer();

      if(!this.uploader.getNotUploadedItems().length){
        deferred.reject('noFilesToUpload');
      } else {
        this.store.getNewId().then(function(data){
          this.id = data.scan_id;
          _.each(this.uploader.getNotUploadedItems(), function(item){
            item.url = this.store.getAddUrl();
          }.bind(this));
          deferred.resolve(data.scan_id);
        }.bind(this), function(){
          deferred.reject('scanIdRetrievalError');
        }.bind(this));
      }
      return deferred.promise;
    };

    ScanModel.prototype.cancelUpload = function(){
      this.uploader.cancelAll();
    };

    ScanModel.prototype.uploadComplete = function(event, items){
      var allGood = true, files = {};
      _.each(this.uploader.queue, function(item){
        files[item.file.name] = {filename: item.file.name};
        if(!item.isSuccess){ allGood = false;}
      });
      $rootScope.$broadcast('uploadComplete', {status: allGood, files: files});
    };

    ScanModel.prototype.launchScan = function(){
      this.scanProgress = {
        progress: 0,
        total: 0,
        successful: 0,
        finished: 0
      };

      return this.store.launchScan().then(function(){
        this.task = $timeout(this.updateScan.bind(this), constants.speed);
      }.bind(this));
    };

    ScanModel.prototype.cancelScan = function(){
      if(this.task){
        $timeout.cancel(this.task);
      }

      return this.store.cancelScan().then(function(data){
        // In scan cancel hook
      }.bind(this));
    };

    ScanModel.prototype.updateScan = function(){
      this.getProgress().then(function(data){
        this.getResults();
        this.task = $timeout(this.updateScan.bind(this), constants.speed);
      }.bind(this), function(data){
        if(data.msg === 'finished'){
          $rootScope.$broadcast('scanComplete');
        } else {
          this.task = $timeout(this.updateScan.bind(this), constants.speed);
        }
      }.bind(this));
    };

    ScanModel.prototype.getProgress = function(){
      return this.store.getProgress().then(function(data){
        this.scanProgress = {
          progress: Math.round(100*data.progress_details.finished / data.progress_details.total),
          total: data.progress_details.total,
          successful: data.progress_details.successful,
          finished: data.progress_details.finished
        };
      }.bind(this));
    };

    ScanModel.prototype.getResults = function(){
      return this.store.getResults().then(function(data){
        console.log(data);
        this.results = this.populateResults(data.scan_results);
      }.bind(this));
    };

    ScanModel.prototype.populateResults = function(data){
      if(!this.baseResults){
        return data;
      }
      
      for(var fileId in data){
        if(data.hasOwnProperty(fileId)){
          data[fileId].results = _.extend({}, this.baseResults, data[fileId].results);
        }
      }

      return data;
    };

    return ScanModel;
  };

  Scan.$inject = dependencies;
  angular.module('irma').factory('ScanModel', Scan);
}());


