'use strict';

(function () {

  var dependencies = [];
  var BooleanDisplay = function () {

    return {
      restrict: 'A',
      scope: {state: '=booleanDisplay', color: '@', text: '@'},
      transclude: true,
      template: '<span '+
        'class="glyphicon glyphicon-{{(state)? \'ok\': \'remove\'}}"'+
        'style="color: {{(color)? color: (state)? \'#5cb85c\': \'#d9534f\'}}"'+
      '></span> <span style="color: {{(color)? color: (state)? \'#5cb85c\': \'#d9534f\'}}" ng-transclude></span>'
    };
  };

  BooleanDisplay.$inject = dependencies;
  angular.module('irma').directive('booleanDisplay', BooleanDisplay);
}());
