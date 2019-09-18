(function () {
  angular
    .module('irma')
    .factory('dataservice', dataservice);

  function dataservice(bridge) {
    return { searchFiles };

    function searchFiles(tags, type, name, offset, limit) {
      let url = '/files?';

      if (tags.length > 0) {
        url += 'tags=';
      }

      for (let i = 0; i < tags.length; i += 1) {
        if (i > 0) {
          url += ',';
        }
        url += tags[i].id;
      }

      if (tags.length > 0) {
        url += '&';
      }

      url += `${type}=${name}&offset=${offset}&limit=${limit}`;

      return bridge.get({ url }).then(searchComplete);

      function searchComplete(response) {
        return response;
      }
    }
  }
}());
