
'use strict';

angular
    .module('irma')
    .factory('dataservice', dataservice);

dataservice.$inject = ['bridge'];

function dataservice(bridge) {
    return {
        searchFiles: searchFiles
    };

    function searchFiles(tags, type, name, offset, limit) {
    	var url = '/search/files?';
    		
    	if (tags.length > 0) {
    		url += 'tags=';
    	}
    	
		for (var i = 0; i < tags.length; i++) {
			if(i > 0) {
				url += ',';
			}
		    url += tags[i].id;
		}
		
    	if (tags.length > 0) {
    		url += '&';
    	}
		
		url += type + '=' + name + '&offset=' + offset + '&limit=' + limit;
		
        return bridge.get({url: url}).then(searchComplete);

        function searchComplete(response) {
            return response;
        }
    }
}
