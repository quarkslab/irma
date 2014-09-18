'use strict';

(function () {

  var dependencies = ['$q', '$rootScope', '$route', '$location', '$timeout', '$log', 'alerts', 'api', 'constants', 'scanModel'];
  var State = function ($q, $rootScope, $route, $location, $timeout, $log, alerts, api, constants, Scan) {

    // Initialize controller
    for (var i = 0; i < dependencies.length; i++){ this[dependencies[i]] = arguments[i];}


    // Variables initialisation
    this.scan = undefined;
    this.probes = [];
    this.settings = {
      force: true,
      maintenance: true,
      loading: true
    };
    this.location = undefined;
    this.status = undefined;
    this.lastAction = undefined;

    // Make state available in all scopes
    $rootScope.state = this;

    // Switch to a new location
    this.goTo = function(path, tail){
      this.status = path;
      this.$location.path('/'+path+((tail)? '/'+tail: ''));
    };

    // Returns the launch params
    this.getLaunchParams = function(){
      var params = {};
      if(this.settings.force){ params.force = true; }
      if(!!_.find(this.probes, {active: false})){ params.probe = _.pluck(_.filter(this.probes, {active: true}), 'name').join(','); }
      return params;
    };

    // Creates new scan
    this.newScan = function(id){
      this.scan = new Scan(id);
      this.scan.setState(this);
    };

    // Retrieves the number of files
    this.nbFiles = function(){
      if(!this.scan){
        return 0;
      } else if(!this.scan.results){
        return this.scan.uploader.queue.length;
      } else {
        return _.size(this.scan.results);
      }
    };








    /*
     *  Probes
     */
    this.loadProbes = function(){
      return api.getProbes().then(function(response){

        if(response.probe_list.length > 0){
          _.forEach(response.probe_list, function(probe){
            this.probes.push({
              name: probe,
              active: true,
              tag: 'Gentille',
              version: 'No version information available'
            });
          }.bind(this));
        } else {
          this.$rootScope.$broadcast('maintenance');
        }
      }.bind(this), function(){
        this.$rootScope.$broadcast('maintenance');
      });
    };
    this.noActiveProbes = function(){
      return !_.find(this.probes, 'active');
    };
    this.probesForScan = function(scan){
      if(!scan.probes){
        console.log('No probes');
      } else {
        return scan.probes;
      }
    };
    this.loadProbes();







    /*
     *  Maintenance check
     */
    this.checkForMaintenance = function(){
      return api.ping().then(function(){
        this.settings.maintenance = false;
        this.settings.loading = false;
      }.bind(this), function(){
        this.settings.loading = false;
      }.bind(this));
    };
    this.pingApi = function(){
      var deferred = $q.defer();

      if(!this.settings.maintenance){
        // The status was already checked, maintenance mode is OFF
        deferred.resolve();
      } else {
        // Checking API status
        this.checkForMaintenance().then(function(){
          // Successfully pinged the API
          deferred.resolve();
        }.bind(this), function(){
          // Switching to maintenance mode
          deferred.reject();
          this.goTo('maintenance');
        }.bind(this));
      }

      return deferred.promise;
    };
    this.noPingApi = function(){
      var deferred = $q.defer();

      if(!this.settings.maintenance){
        // The status was already checked, maintenance mode is OFF
        deferred.reject();
        this.goTo('selection');
      } else if(this.settings.maintenance && !this.settings.loading){
        deferred.resolve();
      } else {
        // Checking API status
        this.checkForMaintenance().then(function(){
          // Successfully pinged the API
          deferred.reject();
          this.goTo('selection');
        }.bind(this), function(){
          // Switching to maintenance mode
          deferred.resolve();
        }.bind(this));
      }

      return deferred.promise;
    };



    this.$rootScope.$on('$routeChangeStart', function(event, newOne, oldOne){
      //this.$log.debug('route change started from '+oldOne.originalPath+' to '+newOne.originalPath);
    }.bind(this));
    this.$rootScope.$on('$routeChangeSuccess', function(event, newOne){
      this.$log.debug('route change success to '+newOne.originalPath);
      this.location = newOne.location;
    }.bind(this));
    this.$rootScope.$on('$routeChangeError', function(event, newOne){
      //this.$log.debug('route change error to '+newOne.originalPath);
    }.bind(this));


    /*
     * Upload events
     */
    this.$rootScope.$on('startUpload', function(){
      this.alerts.add({standard: 'uploadStart'});
      this.scan.startUpload();
      this.goTo('upload');
    }.bind(this));
    this.$rootScope.$on('cancelUpload', function(){
      this.alerts.add({standard: 'uploadCancel'});
      this.goTo('selection');
      this.scan.cancelUpload();
    }.bind(this));
    this.$rootScope.$on('successUpload', function(){
      this.$log.info('Upload was successful');
      if(this.lastAction === 'startUpload'){
        this.alerts.add({standard: 'uploadSuccess'});
        this.$rootScope.$broadcast('startScan');
      }
    }.bind(this));
    this.$rootScope.$on('errorUpload', function(event, msg) {
      this.$log.info('Upload encountered an error');
      this.goTo('selection');
      this.alerts.add({standard: 'apiErrorWithMsg', apiMsg: msg});}
    }.bind(this));


    /*
     * Scan events
     */
    this.$rootScope.$on('startScan', function(){

      $timeout(function(){
        if(this.lastAction === 'startUpload'){
          this.alerts.add({standard: 'scanStart'});
          this.scan.startScan();
          this.goTo('scan');
        } else {
          this.$rootScope.$broadcast('cancelScan');
        }
      }.bind(this), this.constants.speed);
    }.bind(this));
    this.$rootScope.$on('cancelScan', function(){
      this.alerts.add({standard: 'scanCancel'});
      this.goTo('selection');
      this.scan.cancelScan();
    }.bind(this));
    this.$rootScope.$on('successScan', function(){
      this.alerts.add({standard: 'scanSuccess'});
      this.goTo('results', this.scan.id);
      this.scan.getResults();
    }.bind(this));
    this.$rootScope.$on('errorScan', function(){

    }.bind(this));




    this.$rootScope.$on('newScan', function(){

    }.bind(this));
    this.$rootScope.$on('errorResults', function(event, data){
      this.goTo('selection');
    }.bind(this));
    this.$rootScope.$on('maintenance', function(){
      this.settings.maintenance = true;
      this.goTo('maintenance');
    }.bind(this));
  };

  State.$inject = dependencies;
  angular.module('irma').service('state', State);
}());
