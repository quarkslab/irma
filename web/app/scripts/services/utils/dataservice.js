
'use strict';

angular
    .module('irma')
    .factory('dataservice', dataservice);

dataservice.$inject = ['bridge'];

function dataservice(bridge) {
    return {
        searchFiles: searchFiles
    };

    function searchFiles(type, name, page, per_page) {
        return bridge.get({url: '/file/search?' + type + '=' + name + '&page=' + page + '&per_page=' + per_page})
            .then(searchComplete);

        function searchComplete(response) {
            return response;
        }
    }
}
