(function () {
  'use strict';

  angular
    .module('irma')
    .service('api', API);

  API.$inject = ['$q', 'bridge'];

  function API($q, bridge) {
    var service = this;
    service.ping = ping;
    service.getProbes = getProbes;
    service.scan = {
        createNew: createNew,
        getAddUrl: getAddUrl,
        launch: launch,
        cancel: cancel,
        getInfos: getInfos,
        getResults: getResults,
    };
    service.tag = {
    		addTag: addTag,
    		removeTag: removeTag,
	};

    function ping() { return bridge.get({url: '/probes', noAlerts: true}); }
    function getProbes() { return bridge.get({url: '/probes'}); }

    // Scan functions
    function createNew() { return bridge.post({url: '/scans'}); }
    function getAddUrl(scan) {  return bridge.rootUrl + '/scans/' + scan.id + '/files'; }
    function launch(scan, params) { return bridge.post({url: '/scans/' + scan.id + '/launch', payload: params}); }
    function cancel(scan, params) { return bridge.post({url: '/scans/' + scan.id + '/cancel', payload: params}); }
    function getInfos(scan) { return bridge.get({url: '/scans/' + scan.id }); }
    function getResults(scan) { return bridge.get({url: '/scans/' + scan.id + '/results'}); }
    
    // Tag functions
    function addTag(sha256, tagid) { return bridge.get({url: '/files/' + sha256 + '/tags/' + tagid + '/add'}); }
    function removeTag(sha256, tagid) { return bridge.get({url: '/files/' + sha256 + '/tags/' + tagid + '/remove'}); }
  }
}) ();
