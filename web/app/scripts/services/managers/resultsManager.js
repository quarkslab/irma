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
    bridge.get({url: '/scans/' + scanId + '/results/' + fileIdx})
      .then(_loadComplete);

    function _loadComplete(response) {
      var results = _retrieveInstance(response);
      deferred.resolve(results);
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
