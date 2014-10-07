'use strict';

angular
  .module('irma')
  .factory('resultsManager', resultsManager);

resultsManager.$inject = ['$q', '$log', 'Result', 'bridge'];

function resultsManager($q, $log, Result, bridge) {

  return {
    getResult: getResult
  };

  function _load(scanId, fileIdx, deferred) {
    bridge.get({url: '/scan/' + scanId + '/results/' + fileIdx})
      .then(_loadComplete);

    function _loadComplete(response) {
      if (response.code !== -1) {
        var results = _retrieveInstance(response.results);
        deferred.resolve(results);
      }
    }
  }

  function _retrieveInstance(resultData) {
    return new Result(resultData);
  }

  function getResult(scanId, fileIdx) {
    $log.info('Retrieve result');
    var deferred = $q.defer();
    _load(scanId, fileIdx, deferred);

    return deferred.promise;
  }
}
