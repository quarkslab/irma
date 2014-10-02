(function () {
  'use strict';

  angular
    .module('irma')
    .service('state', State);

  State.$inject = ['$q', '$rootScope', '$route', '$location', '$timeout', '$log', 'alerts', 'api', 'constants', 'scanModel'];

  function State($q, $rootScope, $route, $location, $timeout, $log, alerts, api, constants, Scan) {
    var vm = this;
    // Controller Functions definitions
    vm.goTo = goTo;
    vm.getLaunchParams = getLaunchParams;
    vm.newScan = newScan;
    vm.nbFiles = nbFiles;
    vm.loadProbes = loadProbes;
    vm.noActiveProbes = noActiveProbes;
    vm.probesForScan = probesForScan;
    vm.checkForMaintenance = checkForMaintenance;
    vm.pingApi = pingApi;
    vm.noPingApi = noPingApi;
    // Controller variables definitions
    vm.scan = undefined;
    vm.location = undefined;
    vm.status = undefined;
    vm.lastAction = undefined;
    vm.probes = [];
    vm.settings = {
      force: true,
      maintenance: true,
      loading: true
    };

    // Init function
    activate();

    function activate() {
      $rootScope.state = vm;
      vm.loadProbes();
    }

    // Switch to a new location
    function goTo(path, tail) {
      vm.status = path;
      $location.path('/' + path + ((tail) ? '/' + tail : ''));
    }

    // Returns the launch params
    function getLaunchParams() {
      var params = {};

      if(vm.settings.force) {
        params.force = true;
      }

      if(!!_.find(vm.probes, {active: false})) {
        params.probe = _.pluck(_.filter(vm.probes, {active: true}), 'name').join(',');
      }

      return params;
    }

    // Creates new scan
    function newScan(id) {
      vm.scan = new Scan(id);
      vm.scan.setState(vm);
    }

    // Retrieves the number of files
    function nbFiles() {
      if(!vm.scan){
        return 0;
      } else if(!vm.scan.results){
        return vm.scan.uploader.queue.length;
      } else {
        return _.size(vm.scan.results);
      }
    }

    function loadProbes() {
      return api.getProbes().then(function(response) {

        if(response.probe_list.length > 0) {
          _.forEach(response.probe_list, function(probe) {
            vm.probes.push({
              name: probe,
              active: true,
              tag: 'Gentille',
              version: 'No version information available'
            });
          });
        } else {
          $rootScope.$broadcast('maintenance');
        }
      }, function() {
        $rootScope.$broadcast('maintenance');
      });
    }

    function noActiveProbes() {
      return !_.find(vm.probes, 'active');
    }

    function probesForScan(scan) {
      if(!scan.probes){
        $log.info('No probes');
      } else {
        return scan.probes;
      }
    }

    /*
     *  Maintenance check
     */
    function checkForMaintenance() {
      return api.ping().then(function() {
        vm.settings.maintenance = false;
        vm.settings.loading = false;
      }, function() {
        vm.settings.loading = false;
      });
    }

    function pingApi() {
      var deferred = $q.defer();

      if(!vm.settings.maintenance) {
        // The status was already checked, maintenance mode is OFF
        deferred.resolve();
      } else {
        // Checking API status
        vm.checkForMaintenance().then(function() {
          // Successfully pinged the API
          deferred.resolve();
        }, function() {
          // Switching to maintenance mode
          deferred.reject();
          vm.goTo('maintenance');
        });
      }

      return deferred.promise;
    }

    function noPingApi() {
      var deferred = $q.defer();

      if(!vm.settings.maintenance){
        // The status was already checked, maintenance mode is OFF
        deferred.reject();
        vm.goTo('selection');
      } else if(vm.settings.maintenance && !vm.settings.loading) {
        deferred.resolve();
      } else {
        // Checking API status
        vm.checkForMaintenance().then(function() {
          // Successfully pinged the API
          deferred.reject();
          vm.goTo('selection');
        }, function() {
          // Switching to maintenance mode
          deferred.resolve();
        });
      }

      return deferred.promise;
    }

    /**
     * Route events
     */
    $rootScope.$on('$routeChangeStart', function(event, newOne, oldOne) {
      $log.debug('route change started from ' + oldOne.originalPath + ' to ' + newOne.originalPath);
    });

    $rootScope.$on('$routeChangeSuccess', function(event, newOne) {
      $log.debug('route change success to '+ newOne.originalPath);
      vm.location = newOne.location;
    });

    $rootScope.$on('$routeChangeError', function(event, newOne) {
      $log.debug('route change error to ' + newOne.originalPath);
    });

    /*
     * Upload events
     */
    $rootScope.$on('startUpload', function() {
      $log.debug('Start upload');

      alerts.add({standard: 'uploadStart'});
      vm.scan.startUpload();
      vm.goTo('upload');
    });

    $rootScope.$on('cancelUpload', function() {
      $log.debug('Cancel upload');

      alerts.add({standard: 'uploadCancel'});
      vm.goTo('selection');
      vm.scan.cancelUpload();
    });

    $rootScope.$on('successUpload', function() {
      $log.info('Upload was successful');

      if(vm.lastAction === 'startUpload'){
        alerts.add({standard: 'uploadSuccess'});
        $rootScope.$broadcast('startScan');
      }
    });

    $rootScope.$on('errorUpload', function(event, msg) {
      $log.info('Upload encountered an error');
      vm.goTo('selection');
      alerts.add({standard: 'apiErrorWithMsg', apiMsg: msg});
    });

    /*
     * Scan events
     */
    $rootScope.$on('startScan', function() {
      $timeout(function(){
        if(vm.lastAction === 'startUpload') {
          alerts.add({standard: 'scanStart'});
          vm.scan.startScan();
          vm.goTo('scan', vm.scan.id);
        } else {
          $rootScope.$broadcast('cancelScan');
        }
      }, constants.speed);
    });

    $rootScope.$on('cancelScan', function() {
      alerts.add({standard: 'scanCancel'});
      vm.goTo('selection');
      vm.scan.cancelScan();
    });

    $rootScope.$on('successScan', function() {
      alerts.add({standard: 'scanSuccess'});
    });

    $rootScope.$on('errorScan', function() {
      $log.info('Error during scan…');
    });

    $rootScope.$on('newScan', function() {
      $log.info('New scan launched');
    });

    $rootScope.$on('errorResults', function(event, data) {
      vm.goTo('selection');
    });

    $rootScope.$on('maintenance', function(){
      vm.settings.maintenance = true;
      vm.goTo('maintenance');
    });
  }
}) ();
