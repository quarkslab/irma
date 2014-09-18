'use strict';

/*
 *  SCAN MODEL
 */
(function () {

  var dependencies = ['$rootScope', '$fileUploader', '$timeout', '$log', 'api', 'constants'];
  var Scan = function ($rootScope, $fileUploader, $timeout, $log, api, constants) {

    var ScanModel = function(id){
      this.id = id;
      this.state = undefined;
      this.api = api;
      this.task = undefined;
      this.base = undefined;
      this.uploader = $fileUploader.create();
      this.scanProgress = {
        progress: 0,
        total: 0,
        successful: 0,
        finished: 0
      };

      // Bind uploader events
      this.uploader.bind('error',       this.errorUpload.bind(this));
      this.uploader.bind('completeall', this.doneUpload.bind(this));
    };

    ScanModel.prototype.setState = function(state){
      this.state = state;
    };
    ScanModel.prototype.hasFiles = function(){
      return this.uploader.queue.length > 0;
    };
    ScanModel.prototype.buildProbes = function(data){
      var base = {};

      if(data){
        var sample = data[_.keys(data)[0]].results;
        for(var probe in sample){
          if(sample.hasOwnProperty(probe)){
            base[probe] = {result: '__loading__', name: probe, version: sample[probe].version, type: sample[probe].type};
          }
        }
      } else {
        _.forEach(this.state.probes, function(probe){
          if(probe.active){
            base[probe.name] = {result: '__loading__'};
          }
        });
      }

      this.base = base;
    };
    ScanModel.prototype.getPopover = function(probe, results){
      if(results.status === 0 || results.status === '0'){
        return {
          title: probe,
          content: 'File clean'
        };
      } else if(results.status === 1 || results.status === '1'){
        return {
          title: probe,
          content: 'File compromised'
        };
      } else if(results.status === 'loading'){
        return {
          title: probe,
          content: 'Waiting for response'
        };
      } else {
        return {
          title: probe,
          content: 'An error occured'
        };
      }
    };


    /*
     *  Upload handling:
     *  - Start:   Retrieves a scan id, sets the files url, start uploading
     *  - Cancel:  Stops the upload
     *  - Error:   Broadcasts the event
     *  - Done:    Checks for errors, broadcasts the appropriate event
     */
    ScanModel.prototype.startUpload = function(){
      this.buildProbes();
      this.api.scan.getNewId().then(function(response){
        this.id = response.scan_id;
        var items = this.uploader.getNotUploadedItems();
        _.each(items, function(item){
          item.url = this.api.scan.getAddUrl(this);
        }.bind(this));
        $log.info('Upload has started');
        this.uploader.uploadAll();
      }.bind(this));
    };
    ScanModel.prototype.cancelUpload = function(){
      $log.info('Upload was cancelled');
      this.uploader.cancelAll();
    };
    ScanModel.prototype.errorUpload = function(){
      $rootScope.$broadcast('errorUpload');
    };
    ScanModel.prototype.doneUpload = function(event, items){
      if(!!_.find(items, function(item){ return (!item.isSuccess || JSON.parse(item._xhr.response).code !== 0); })){
        this.errorUpload();
      } else {
        $rootScope.$broadcast('successUpload');
      }
    };





    ScanModel.prototype.startScan = function(){
      var params = this.state.getLaunchParams();
      $log.info('Scan was launched');
      this.api.scan.launch(this, params).then(function(response){
        this.updateScan();
      }.bind(this));
    };
    ScanModel.prototype.cancelScan = function(){
      $log.info('Scan was cancelled');
      $timeout.cancel(this.task);
      if(this.id){
        this.api.scan.cancel(this);
      }
    };
    ScanModel.prototype.updateScan = function(){
      if(this.state.lastAction !== 'startUpload'){
        return false;
      }

      this.api.scan.getProgress(this).then(function(data){
        if(data.code === 0){
          if(data.progress_details.finished !== this.scanProgress.finished){
            this.setProgress(data);
            this.getResults();
          }
          this.task = $timeout(this.updateScan.bind(this), constants.refresh);
        } else {
          if(data.msg === 'finished'){
            $log.info('Scan was successful');
            this.scanProgress.progress = 100;
            this.scanProgress.successful = this.scanProgress.total;
            this.scanProgress.finished = this.scanProgress.total;
            $rootScope.$broadcast('successScan');
          } else {
            this.task = $timeout(this.updateScan.bind(this), constants.refresh);
          }
        }
      }.bind(this));
    };
    ScanModel.prototype.setProgress = function(data){
      this.scanProgress = {
        progress: Math.round(100*data.progress_details.finished / data.progress_details.total),
        total: data.progress_details.total,
        successful: data.progress_details.successful,
        finished: data.progress_details.finished
      };
    };
    ScanModel.prototype.getResults = function(){
      $log.info('Updating results');
      return this.api.scan.getResults(this).then(function(data){
        this.results = data.scan_results; //this.populateResults(data.scan_results);
        this.buildAntivirus();
      }.bind(this), function(data){
        $rootScope.$broadcast('errorResults', data);
      }.bind(this));
    };
    ScanModel.prototype.populateResults = function(data){
      if(!this.base){
        this.buildProbes(data);
      }

      for(var fileId in data){
        if(data.hasOwnProperty(fileId)){
          data[fileId].results = _.extend({}, this.base, data[fileId].results);
        }
      }
      return data;
    };
    ScanModel.prototype.buildAntivirus = function(){
      this.antivirus = {};
      this.antivirusProbes = {};
      _.forOwn(this.results, function(fileData, fileId){
        _.forOwn(fileData.results, function(probeData, probeName){
          if(probeData.type === 'antivirus'){
            this.antivirusProbes[probeName] = _.pick(probeData, ['name', 'type', 'version']);
          }
        }, this);
      }.bind(this), this);

      _.forOwn(this.results, function(fileData, fileId){
        this.antivirus[fileId] = _.omit(fileData, 'results');
        this.antivirus[fileId].results = {};
        _.forOwn(this.antivirusProbes, function(probeData, probeName){
          if(_.has(fileData.results, probeName) && fileData.results[probeName].result !== '__loading__'){
            this.antivirus[fileId].results[probeName] = fileData.results[probeName];
          } else {
            this.antivirus[fileId].results[probeName] = {status: 'loading'};
          }
        }, this);
      }, this);
    };

    return ScanModel;
  };

  Scan.$inject = dependencies;
  angular.module('irma').factory('scanModel', Scan);
}());


