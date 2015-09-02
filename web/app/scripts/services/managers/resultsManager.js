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

  function _load(resultId, deferred) {
    bridge.get({url: '/results/' + resultId })
      .then(_loadComplete);

    function _loadComplete(response) {
      var results = _retrieveInstance(response);
      deferred.resolve(results);
    }
  }

  function _retrieveInstance(resultData) {
    return new Result(resultData);
  }

  function getResult(resultId) {
    $log.info('Retrieve result');
    var deferred = $q.defer();
    _load(resultId, deferred);

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
