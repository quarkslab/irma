'use strict';

(function () {

  var dependencies = [];
  var fileTrigger = function () {

    return {
      link: function(scope, element, attr) {
        element.click(function(){
          angular.element('#file-container').click();
        });
      }
    };
  };

  fileTrigger.$inject = dependencies;
  angular.module('irma').directive('fileTrigger', fileTrigger);
}());
