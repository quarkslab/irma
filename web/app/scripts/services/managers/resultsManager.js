'use strict';

angular
  .module('irma')
  .factory('resultsManager', resultsManager);

resultsManager.$inject = ['$q', '$log', 'Result', 'bridge'];

function resultsManager($q, $log, Result, bridge) {

  return {
    getResult: getResult,
    getAvailableTags: getAvailableTags
  };

  function _loadResult(scanId, fileIdx, deferred) {
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
    _loadResult(scanId, fileIdx, deferred);

    return deferred.promise;
  }
  
  function getAvailableTags() {
    $log.info('Retrieve available tags');
    var deferred = $q.defer();
    _loadAvailableTags(deferred);

    return deferred.promise;
  }
  
  function _loadAvailableTags(deferred) {
    bridge.get({url: '/tags'})
      .then(_loadComplete);

    function _loadComplete(response) {
      var results = _retrieveInstance(response);
      deferred.resolve(results);
    }
  }
}
