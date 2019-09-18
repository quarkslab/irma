(function () {
  angular
    .module('irma')
    .service('state', State);

  function State(
    $q, $rootScope, $route, $location, $timeout, $log,
    api, constants, UploadModel, ScanModel,
  ) {
    // Exports
    const service = this;
    angular.extend(service, {
      // Variables
      uploader: undefined,
      scan: undefined,
      location: undefined,
      status: undefined,
      lastAction: undefined,
      domain: `${$location.protocol()}://${$location.host()}`,
      title: 'IRMA',
      probes: [],
      settings: {
        force: true,
        loading: true,
        maintenance: false,
      },
      // Functions
      goTo,
      newUploader,
      newScan,
      noActiveProbes,
      updateTitle,
    });
    // Controller variables definitions

    // IIFE when entering the service
    (function run() {
      angular.extend($rootScope, { state: service });

      api
        .ping()
        .then(() => { loadProbes(); })
        .catch(() => { $rootScope.$broadcast('maintenance'); })
        .finally(() => { service.settings.loading = false; });
    }());

    // Switch to a new location
    function goTo(path, tail) {
      service.status = path;
      $location.path(`/${path}${(tail) ? `/${tail}` : ''}`);
    }

    // Creates new Uploader
    function newUploader() {
      service.uploader = new UploadModel();
    }

    // Creates new scan
    function newScan(id) {
      service.scan = new ScanModel(id);
    }

    function loadProbes() {
      return api.getProbes().then((response) => {
        if (response.total > 0) {
          _.forEach(response.data, (probe) => {
            service.probes.push({
              name: probe,
              active: true,
              tag: 'Gentille',
              version: 'No version information available',
            });
          });
        } else {
          $rootScope.$broadcast('maintenance');
        }
      }, () => {
        $rootScope.$broadcast('maintenance');
      });
    }

    function noActiveProbes() {
      return !_.find(service.probes, 'active');
    }

    function updateTitle() {
      service.title = (service.location) ? `IRMA | ${service.location[0].toUpperCase()}${service.location.slice(1)}` : 'IRMA';
    }

    /**
     * Private methods
     */

    // Returns the launch params
    function getLaunchParams() {
      const params = {
        force: service.settings.force,
        probes: [],
      };

      service.probes.forEach((probe) => {
        if (probe.active) {
          params.probes.push(probe.name);
        }
      });

      return params;
    }

    /*
     * Scan events
     */
    $rootScope.$on('startScan', () => {
      newScan();
      service.scan.launch({
        files: service.uploader.extractFilesExtId(),
        options: getLaunchParams(),
      }).then(() => {
        service.goTo('scan', service.scan.id);
      });
    });

    $rootScope.$on('cancelScan', () => {
      service.goTo('selection');
      service.scan.cancelScan();
    });

    $rootScope.$on('errorScan', () => { $log.info('Error during scan!'); });
    $rootScope.$on('errorResults', () => { service.goTo('selection'); });
  }
}());
