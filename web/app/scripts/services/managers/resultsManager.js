'use strict';

angular
  .module('irma')
  .factory('resultsManager', resultsManager);

resultsManager.$inject = ['$http', '$q', '$log', 'Result'];

function resultsManager($http, $q, $log, Result) {

  return {
    getResult: getResult
  };

  function _load(scanId, resultId, deferred) {
    $http.get('_api/scan/' + scanId + '/results/' + resultId)
      .success(_loadComplete)
      .catch(_loadFailed);

    function _loadComplete(response) {
      var result = _retrieveInstance(response.result);
      deferred.resolve(result);
    }

    function _loadFailed(error) {
      $log.error('XHR failed for _load result:' + error.data);
    }
  }

  function _retrieveInstance(resultData) {
    return new Result(resultData);
  }

  function getResult(scanId, resultId) {
    $log.info('Retrieve result');
    var deferred = $q.defer();
    _load(scanId, resultId, deferred);

    return deferred.promise;
  }
}
