'use strict';

angular.module('irma')
.directive('fileTrigger', [function() {
  return {
    link: function(scope, element, attr) {
      element.click(function(){
        $('#file-container').click();
      });
    }
  };
}]);

angular.module('irma')
.directive('booleanDisplay', [function() {
  return {
    restrict: 'A',
    scope: {state: '=booleanDisplay'},
    template: '<span class="glyphicon glyphicon-{{(state)? \'ok\': \'remove\'}}" style="color: {{(state)? \'#5cb85c\': \'#d9534f\'}}"></span>'
  };
}]);