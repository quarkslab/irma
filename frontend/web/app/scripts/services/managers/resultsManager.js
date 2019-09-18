(function () {
  angular
    .module('irma')
    .factory('resultsManager', resultsManager);

  function resultsManager($q, Result, api) {
    // Exports
    return {
      getResult,
      getAvailableTags,
    };

    // Functions
    function load(resultId, deferred) {
      api.files.details(resultId)
        .then(loadComplete);

      function loadComplete(response) {
        const results = retrieveInstance(response);
        deferred.resolve(results);
      }
    }

    function retrieveInstance(resultData) {
      return new Result(resultData);
    }

    function getResult(resultId) {
      const deferred = $q.defer();
      load(resultId, deferred);

      return deferred.promise;
    }

    function getAvailableTags() {
      const deferred = $q.defer();
      loadAvailableTags(deferred);

      return deferred.promise;
    }

    function loadAvailableTags(deferred) {
      api.tag.list()
        .then(loadComplete);

      function loadComplete(response) {
        const results = retrieveInstance(response);
        deferred.resolve(results);
      }
    }
  }
}());
