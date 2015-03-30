
'use strict';

angular
    .module('irma')
    .factory('dataservice', dataservice);

dataservice.$inject = ['bridge'];

function dataservice(bridge) {
    return {
        searchFiles: searchFiles
    };

    function searchFiles(type, name, offset, limit) {
        return bridge.get({url: '/search/files?' + type + '=' + name + '&offset=' + offset + '&limit=' + limit})
            .then(searchComplete);

        function searchComplete(response) {
            return response;
        }
    }
}
