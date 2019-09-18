(function () {
  angular
    .module('irma')
    .service('bridge', Bridge);

  function Bridge($http, $q, $timeout, alerts, constants) {
    // Exports
    const service = this;
    angular.extend(service, {
      rootUrl: constants.baseApi,

      get,
      post,
    });

    // Functions
    function get(options) {
      const deferred = $q.defer();

      $http.get(service.rootUrl + options.url, { params: options.payload }).then((response) => {
        $timeout(() => {
          deferred.resolve(response.data);
        }, constants.fakeDelay);
      }, (response) => {
        // In case of error with the API
        if (!options.noAlerts) {
          alerts.add(`API Error: ${response.data.errors}`, 'danger');
        }

        $timeout(() => { deferred.reject(response.data); }, constants.fakeDelay);
      });

      return deferred.promise;
    }

    function post(options) {
      const deferred = $q.defer();

      $http.post(service.rootUrl + options.url, options.payload).then((response) => {
        $timeout(() => { deferred.resolve(response.data); }, constants.fakeDelay);
      }, (response) => {
        // In case of error with the API
        if (!options.noAlerts) {
          alerts.add(`API Error: ${response.data.errors}`, 'danger');
        }

        $timeout(() => { deferred.reject(response.data); }, constants.fakeDelay);
      });

      return deferred.promise;
    }
  }
}());
