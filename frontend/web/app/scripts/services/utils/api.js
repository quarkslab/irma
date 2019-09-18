(function () {
  angular
    .module('irma')
    .service('api', API);

  function API($q, bridge) {
    const service = this;

    angular.extend(service, {
      ping,
      getProbes,
      scan: {
        launch,
        cancel,
        getInfos,
        getResults,
      },
      files: {
        upload,
        details,
      },
      tag: {
        list,
        addTag,
        removeTag,
      },
    });

    function ping() { return bridge.get({ url: '/about', noAlerts: true }); }
    function getProbes() { return bridge.get({ url: '/probes' }); }

    // Scan functions
    function launch(params) { return bridge.post({ url: '/scans', payload: params }); }
    function cancel(scan, params) { return bridge.post({ url: `/scans/${scan.id}/cancel`, payload: params }); }
    function getInfos(scan) { return bridge.get({ url: `/scans/${scan.id}` }); }
    function getResults(scan) { return bridge.get({ url: `/scans/${scan.id}/results` }); }

    // Files functions
    function upload(playload) { return bridge.post({ url: '/files_ext', playload }); }
    function details(id) { return bridge.get({ url: `/files_ext/${id}` }); }


    // Tag functions
    function list() { return bridge.get({ url: '/tags' }); }
    function addTag(sha256, tagid) { return bridge.get({ url: `/files/${sha256}/tags/${tagid}/add` }); }
    function removeTag(sha256, tagid) { return bridge.get({ url: `/files/${sha256}/tags/${tagid}/remove` }); }
  }
}());
