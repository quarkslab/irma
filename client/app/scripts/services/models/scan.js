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
            item.url = this.store.getAddUrl(this.id);
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
        if(!item.isSuccess) allGood = false;
      });
      $rootScope.$broadcast('uploadComplete', {status: allGood, files: files});
    };

    ScanModel.prototype.launchScan = function(){

      return this.store.launchScan().then(function(){
        $timeout(this.updateScan.bind(this), constants.speed);
      }.bind(this));
    };

    ScanModel.prototype.cancelScan = function(){
      return this.store.cancelScan().then(function(data){
        this.scanProgress = 0;
      }.bind(this));
    };

    ScanModel.prototype.updateScan = function(){
      console.log('coucou, je suis updaté!');

      $timeout(this.updateScan.bind(this), constants.speed);
    };

    return ScanModel;
  };

  Scan.$inject = dependencies;
  angular.module('irma').factory('ScanModel', Scan);
}());


